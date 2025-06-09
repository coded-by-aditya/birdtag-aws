import json
import os
import boto3
import cv2
import numpy as np
from tempfile import NamedTemporaryFile
from ultralytics import YOLO

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdnetTaggedFiles')

model = YOLO("model.pt")
class_dict = model.names

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

def get_file_type(path):
    ext = os.path.splitext(path)[-1].lower()
    if ext in ['.jpg', '.jpeg', '.png']:
        return 'image'
    elif ext in ['.mp4', '.avi', '.mov']:
        return 'video'
    return 'unknown'

def convert_to_https(s3_uri):
    if not s3_uri.startswith("s3://"):
        return s3_uri
    parts = s3_uri[5:].split('/', 1)
    bucket = parts[0]
    key = parts[1]
    region = "us-east-1"
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

def lambda_handler(event, context):
    try:
        content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
        if not content_type or 'multipart/form-data' not in content_type.lower():
            return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid content type'})}

        body = event.get("body")
        if event.get("isBase64Encoded"):
            import base64
            body = base64.b64decode(body)

        with NamedTemporaryFile(delete=False, suffix=".tmp") as tmp_file:
            tmp_file.write(body)
            tmp_path = tmp_file.name

        ext = get_file_type(tmp_path)
        if ext == "image":
            img = cv2.imread(tmp_path)
            if img is None:
                raise Exception("Could not read image")
            tags = tag_image(img)
        elif ext == "video":
            tags = tag_video(tmp_path)
        else:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Unsupported file type'})}

        os.remove(tmp_path)

        if not tags:
            return {'statusCode': 200, 'body': json.dumps({'tags': {}, 'links': []})}

        detected_species = set(tags.keys())
        response = table.scan()
        matched_links = []

        for item in response['Items']:
            item_tags = item.get('tags', {})
            if any(tag in item_tags for tag in detected_species):
                if item['file_type'] == 'images' and item.get('thumbnail_url'):
                    matched_links.append(convert_to_https(item['thumbnail_url']))
                else:
                    matched_links.append(convert_to_https(item['original_url']))

        return {
            'statusCode': 200,
            'body': json.dumps({'tags': tags, 'links': matched_links})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
