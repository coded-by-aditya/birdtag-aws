import boto3
import os
import tempfile
from PIL import Image
import PIL.Image

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Get bucket name and object key
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Download file from S3
    download_path = os.path.join(tempfile.gettempdir(), os.path.basename(key))
    s3.download_file(bucket, key, download_path)
    
    # Create thumbnail using Pillow
    thumbnail_path = os.path.join(tempfile.gettempdir(), f"thumb-{os.path.basename(key)}")
    with Image.open(download_path) as img:
        img.thumbnail((128, 128))  # Resize maintaining aspect ratio
        img.save(thumbnail_path, format="JPEG", quality=85)
    
    # Upload thumbnail back to S3
    thumbnail_key = f"thumbnails/thumb-{os.path.basename(key)}"
    s3.upload_file(thumbnail_path, bucket, thumbnail_key)
    
    return {
        'statusCode': 200,
        'body': f'Thumbnail created: {thumbnail_key}'
    }