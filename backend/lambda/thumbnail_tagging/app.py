import json
import os
import boto3
import cv2
import numpy as np
from urllib.parse import unquote_plus
from ultralytics import YOLO

# AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdnetTaggedFiles')

# S3 model location
MODEL_BUCKET = "birdfile-models"
MODEL_KEY = "models/yolo/model.pt"
MODEL_LOCAL_PATH = "/tmp/model.pt"

# Model will be loaded on cold start
model = None
class_dict = None

def load_model():
    global model, class_dict
    if model is None:
        if not os.path.exists(MODEL_LOCAL_PATH):
            print("Downloading model from S3...")
            s3.download_file(MODEL_BUCKET, MODEL_KEY, MODEL_LOCAL_PATH)
        model = YOLO(MODEL_LOCAL_PATH)
        class_dict = model.names

def resize_image(image, width=128):
    h, w = image.shape[:2]
    new_h = int((width / w) * h)
    return cv2.resize(image, (width, new_h))

def tag_image(img):
    result = model(img)[0]
    counts = {}
    for cls_id, conf in zip(result.boxes.cls.cpu().numpy(), result.boxes.conf.cpu().numpy()):
        if conf > 0.5:
            species = class_dict[int(cls_id)].lower()
            counts[species] = counts.get(species, 0) + 1
    return counts

def tag_video(video_path):
    cap = cv2.VideoCapture(video_path)
    species_tracker = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        result = model(frame)[0]
        frame_counts = {}
        for cls_id, conf in zip(result.boxes.cls.cpu().numpy(), result.boxes.conf.cpu().numpy()):
            if conf > 0.5:
                species = class_dict[int(cls_id)].lower()
                frame_counts[species] = frame_counts.get(species, 0) + 1

        for species, count in frame_counts.items():
            if species not in species_tracker or count > species_tracker[species]:
                species_tracker[species] = count

    cap.release()
    return species_tracker

def lambda_handler(event, context):
    load_model()

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        base_name = os.path.basename(key)
        file_type = key.split('/')[0].lower()

        tmp_input = f"/tmp/{base_name}"
        s3.download_file(bucket, key, tmp_input)

        thumbnail_url = None
        tags = {}

        if file_type == "images":
            img = cv2.imread(tmp_input)
            if img is None:
                print(f"Failed to load image: {key}")
                continue

            # Create thumbnail
            thumb = resize_image(img)
            thumb_name = os.path.splitext(base_name)[0] + "-thumb.jpg"
            thumb_path = f"/tmp/{thumb_name}"
            cv2.imwrite(thumb_path, thumb)

            thumb_key = f"thumbnails/{thumb_name}"
            s3.upload_file(thumb_path, bucket, thumb_key, ExtraArgs={'ContentType': 'image/jpeg'})
            thumbnail_url = f"s3://{bucket}/{thumb_key}"

            tags = tag_image(img)

        elif file_type == "videos":
            tags = tag_video(tmp_input)

        elif file_type == "audio":
            tags = {"status": "audio_processing_pending"}

        else:
            print(f"Unsupported file type for key: {key}")
            continue

        item = {
            "file_id": base_name,
            "file_type": file_type,
            "original_url": f"s3://{bucket}/{key}",
            "tags": {k: int(v) for k, v in tags.items()},
            "thumbnail_url": thumbnail_url
        }

        table.put_item(Item=item)
        print(f"Metadata written to DynamoDB: {item}")

    return {
        "statusCode": 200,
        "body": json.dumps("File processed.")
    }
