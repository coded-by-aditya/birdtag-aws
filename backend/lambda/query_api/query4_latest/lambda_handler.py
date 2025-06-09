import json
import os
import boto3
import cv2
from ultralytics import YOLO
from collections import Counter
import subprocess
import zipfile
import time

# AWS resources
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdMediaMetadata')

# Model S3 info
MODEL_BUCKET = "birdtag-storage-aus-dev"
MODEL_KEY = "models/video/model.pt"
MODEL_LOCAL_PATH = "/tmp/model.pt"

# BirdNET S3 info
BIRDNET_BUCKET = "birdtag-storage-aus-dev"
BIRDNET_ZIP_KEY = "models/audio/birdnet_analyzer.zip"
BIRDNET_LOCAL_DIR = "/tmp/birdnet"

# Model cache
model = None
class_dict = {}

def load_model():
    global model, class_dict
    if model is None:
        if not os.path.exists(MODEL_LOCAL_PATH):
            print("Downloading YOLO model from S3...")
            s3.download_file(MODEL_BUCKET, MODEL_KEY, MODEL_LOCAL_PATH)
        model = YOLO(MODEL_LOCAL_PATH)
        class_dict.clear()
        class_dict.update(model.names)
        print("YOLO model loaded.")

def get_file_extension(filename):
    return os.path.splitext(filename)[-1].lower()

def convert_to_https(s3_uri):
    if not s3_uri.startswith("s3://"):
        return s3_uri
    parts = s3_uri[5:].split('/', 1)
    bucket, key = parts
    region = "us-east-1"
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

def prepare_birdnet_dir():
    if not os.path.exists(BIRDNET_LOCAL_DIR):
        print("Downloading and extracting BirdNET-Analyzer...")
        s3.download_file(BIRDNET_BUCKET, BIRDNET_ZIP_KEY, '/tmp/birdnet_analyzer.zip')
        with zipfile.ZipFile('/tmp/birdnet_analyzer.zip', 'r') as zip_ref:
            zip_ref.extractall(BIRDNET_LOCAL_DIR)

def analyze_audio(input_wav_path, output_dir, birdnet_dir):
    cmd = [
        "python3", "-m", "birdnet_analyzer.analyze",
        os.path.dirname(input_wav_path), "-o", output_dir
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=birdnet_dir)
    print(result.stdout)
    print(result.stderr)
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

def tag_image(img):
    result = model(img)[0]
    counts = {}
    for cls_id, conf in zip(result.boxes.cls.cpu().numpy(), result.boxes.conf.cpu().numpy()):
        if conf > 0.5:
            species = class_dict[int(cls_id)].lower()
            counts[species] = counts.get(species, 0) + 1
    return counts

def tag_video(path):
    cap = cv2.VideoCapture(path)
    species_tracker = {}
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        result = model(frame)[0]
        for cls_id, conf in zip(result.boxes.cls.cpu().numpy(), result.boxes.conf.cpu().numpy()):
            if conf > 0.5:
                species = class_dict[int(cls_id)].lower()
                species_tracker[species] = species_tracker.get(species, 0) + 1
    cap.release()
    return species_tracker

def lambda_handler(event, context):
    global model, class_dict
    try:
        # Get file info from S3 event
        record = event["Records"][0]
        file_bucket = record["s3"]["bucket"]["name"]
        file_key = record["s3"]["object"]["key"]

        print(f"Received S3 event for: s3://{file_bucket}/{file_key}")

        # Get file extension and type
        filename = os.path.basename(file_key)
        ext = get_file_extension(filename)
        file_type = (
            'image' if ext in ['.jpg', '.jpeg', '.png']
            else 'video' if ext in ['.mp4', '.avi', '.mov']
            else 'audio' if ext in ['.wav', '.flac', '.mp3']
            else None
        )
        if file_type is None:
            print(f"Unsupported file type: {ext}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Unsupported file type'})
            }

        # Download file to /tmp
        tmp_path = f"/tmp/{filename}"
        s3.download_file(file_bucket, file_key, tmp_path)
        print(f"Downloaded {file_key} from bucket {file_bucket} to {tmp_path}")

        tags = {}

        if file_type in ["image", "video"]:
            load_model()

        if file_type == "image":
            img = cv2.imread(tmp_path)
            if img is None:
                raise Exception("cv2 failed to load image")
            tags = tag_image(img)
        elif file_type == "video":
            tags = tag_video(tmp_path)
        elif file_type == "audio":
            prepare_birdnet_dir()
            output_dir = "/tmp/audio_output"
            os.makedirs(output_dir, exist_ok=True)
            tags = analyze_audio(tmp_path, output_dir, BIRDNET_LOCAL_DIR)

        os.remove(tmp_path)
        print("Detected tags:", tags)

        if not tags:
            return {
                'statusCode': 200,
                'body': json.dumps({'tags': {}, 'links': []}),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }

        # Lookup in DynamoDB
        detected_species = set(tags.keys())
        response = table.scan()
        matched_links = []
        for item in response.get('Items', []):
            item_tags = item.get('tags', {})
            if any(tag in item_tags for tag in detected_species):
                if item.get('file_type') == 'image' and item.get('thumbnail_url'):
                    matched_links.append(convert_to_https(item['thumbnail_url']))
                elif item.get('original_url'):
                    matched_links.append(convert_to_https(item['original_url']))

        print("Matched links:", matched_links)

        # Delete the uploaded file from S3
        s3.delete_object(Bucket=file_bucket, Key=file_key)
        print(f"Deleted original file s3://{file_bucket}/{file_key} from S3.")

        results_table = dynamodb.Table("TempQueryResults")
        results_table.put_item(Item={
            'file_key': file_key,
            'tags': tags,
            'links': matched_links,
            'ttl': int(time.time()) + 300  # optional: expire in 30 minutes
        })

        return {
            'statusCode': 200,
            'body': json.dumps({'tags': tags, 'links': matched_links}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    except Exception as e:
        print("Unhandled exception:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
    

