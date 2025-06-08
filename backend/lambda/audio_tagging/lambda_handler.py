import os
import boto3
import subprocess
import zipfile
import sys
from collections import Counter

os.environ["NUMBA_CACHE_DIR"] = "/tmp/numba_cache"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("BirdnetTaggedFiles")  # Use your DynamoDB table name

def download_from_s3(bucket, key, dest):
    """Download a file from S3 to local path."""
    s3 = boto3.client('s3')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    s3.download_file(bucket, key, dest)

def download_and_extract_zip_from_s3(bucket, key, extract_to):
    """Download and extract a zip file from S3 to a target directory."""
    s3 = boto3.client('s3')
    zip_path = '/tmp/birdnet_analyzer.zip'
    s3.download_file(bucket, key, zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def analyze_audio(input_wav_path, output_dir, birdnet_dir):
    """
    Run BirdNET-Analyzer CLI on a single audio file, returning a dict {species_name: count}.
    Assumes all dependencies and resources are available in birdnet_dir.
    """
    # Add BirdNET directory to sys.path if not already present
    if birdnet_dir not in sys.path:
        sys.path.insert(0, birdnet_dir)
    # Ensure output dir exists
    os.makedirs(output_dir, exist_ok=True)
    input_dir = os.path.dirname(input_wav_path)
    cmd = [
        "python3", "-m", "birdnet_analyzer.analyze",
        input_dir, "-o", output_dir,
    ]
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    # Parse tags from output
    species_counter = Counter()
    for fname in os.listdir(output_dir):
        if fname.endswith(".txt"):
            with open(os.path.join(output_dir, fname)) as f:
                for line in f:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) > 7:
                        species_name = parts[7]
                        if species_name.strip().lower() == "common name":
                            continue
                        species_counter[species_name] += 1
    return dict(species_counter)

def write_tags_to_dynamodb(base_name, file_type, s3_url, tags, table):
    """Write result to DynamoDB."""
    item = {
        "file_id": base_name,
        "file_type": file_type,
        "original_url": s3_url,
        "tags": {k: int(v) for k, v in tags.items()},
    }
    table.put_item(Item=item)
    print(f"Wrote result to DynamoDB: {item}")
    return item

def prepare_birdnet_dir(birdnet_bucket, birdnet_zip_key, birdnet_dir):
    """Download and extract BirdNET-Analyzer if not already present."""
    if not os.path.exists(birdnet_dir):
        print("Downloading and extracting BirdNET-Analyzer...")
        download_and_extract_zip_from_s3(birdnet_bucket, birdnet_zip_key, birdnet_dir)

def prepare_audio_file(audio_bucket, audio_key, input_dir):
    """Download the input audio file from S3 to the specified directory."""
    os.makedirs(input_dir, exist_ok=True)
    audio_local_path = os.path.join(input_dir, "input.wav")
    download_from_s3(audio_bucket, audio_key, audio_local_path)
    print("Completed audio download")
    return audio_local_path

# --- Main Lambda Handler ---
def lambda_handler(event, context):
    birdnet_bucket = "birdnet-model-178"
    birdnet_zip_key = "birdnet_analyzer.zip"
    birdnet_dir = "/tmp/birdnet"
    input_dir = "/tmp/input_audio"
    output_dir = "/tmp/output"

    # 1. Ensure BirdNET-Analyzer is in /tmp/birdnet
    prepare_birdnet_dir(birdnet_bucket, birdnet_zip_key, birdnet_dir)

    # 2. Parse event for audio file info and download it
    record = event["Records"][0]
    audio_bucket = record["s3"]["bucket"]["name"]
    audio_key = record["s3"]["object"]["key"]
    audio_local_path = prepare_audio_file(audio_bucket, audio_key, input_dir)

    # 3. Analyze audio file and get species tag counts
    tags = analyze_audio(audio_local_path, output_dir, birdnet_dir)
    print(f"Species counts: {tags}")

    # 4. Store in DynamoDB
    base_name = os.path.splitext(os.path.basename(audio_key))[0]
    file_type = os.path.splitext(audio_key)[1].lstrip('.').lower()
    s3_url = f"s3://{audio_bucket}/{audio_key}"
    item = write_tags_to_dynamodb(base_name, file_type, s3_url, tags, table)
    return item
