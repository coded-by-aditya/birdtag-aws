import os
import boto3
import subprocess
from collections import Counter

os.environ["NUMBA_CACHE_DIR"] = "/tmp/numba_cache"

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("BirdnetTaggedFiles")  # Use your DynamoDB table name

def download_from_s3(bucket, key, dest):
    s3 = boto3.client('s3')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    s3.download_file(bucket, key, dest)

def lambda_handler(event, context):
    # Parse S3 event to get uploaded audio file info
    record = event["Records"][0]
    audio_bucket = record["s3"]["bucket"]["name"]
    audio_key = record["s3"]["object"]["key"]

    # Set local temp file locations
    input_dir = "/tmp/input_audio"
    output_dir = "/tmp/output"
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    audio_local_path = os.path.join(input_dir, "input.wav")

    # Download the audio file from S3
    download_from_s3(audio_bucket, audio_key, audio_local_path)
    print("Completed audio download")

    print("Starting analysis")
    # Run BirdNET-Analyzer CLI on the audio file
    result = subprocess.run(
        [
            "python3", "-m", "birdnet_analyzer.analyze",
            input_dir, "-o", output_dir
        ],
        capture_output=True, text=True
    )
    print("Finished analysis")
    print(result.stdout)
    print(result.stderr)

    # Parse species counts from output file(s)
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

    print(f"Species counts: {species_counter}")

    base_name = os.path.splitext(os.path.basename(audio_key))[0]
    file_type = os.path.splitext(audio_key)[1].lstrip('.').lower()

    item = {
        "file_id": base_name,
        "file_type": file_type,
        "original_url": f"s3://{audio_bucket}/{audio_key}",
        "tags": {k: int(v) for k, v in species_counter.items()},
    }

    table.put_item(Item=item)
    print(f"Wrote result to DynamoDB: {item}")

    return item
