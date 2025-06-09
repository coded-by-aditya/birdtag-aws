import boto3
import os
import json
import urllib.parse

s3 = boto3.client('s3')
BUCKET_NAME = "birdtag-storage-aus-dev"

def lambda_handler(event, context):
    try:
        filename = event["queryStringParameters"]["filename"]
        decoded_filename = urllib.parse.unquote(filename)
        ext = os.path.splitext(decoded_filename)[1].lower()

        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            folder = "images"
        elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
            folder = "videos"
        elif ext in ['.mp3', '.wav', '.aac', '.flac']:
            folder = "audios"
        else:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Unsupported file type'})
            }

        key = f"{folder}/{decoded_filename}"

        url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': key,
                'ContentType': event["queryStringParameters"].get("content_type", "application/octet-stream")
            },
            ExpiresIn=3600
        )

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'upload_url': url})
        }

    except Exception as e:
        print("Error:", e)
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }