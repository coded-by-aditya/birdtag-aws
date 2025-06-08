import json
import boto3
from urllib.parse import urlparse

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamodb.Table('BirdnetTaggedFiles')

def lambda_handler(event, context):
    try:
        if 'body' in event and isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event

        urls = body.get('url', [])
        if not isinstance(urls, list):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid input structure'})
            }

        deleted_files = []
        all_items = table.scan().get('Items', [])

        for url in urls:
            s3_key = extract_s3_key(url)
            if not s3_key:
                continue

            # Match against original_url only
            matched_item = next(
                (item for item in all_items if s3_key in item.get('original_url', '')),
                None
            )

            if not matched_item:
                continue

            # Delete original file from S3
            delete_s3_object(matched_item['original_url'])

            # Delete thumbnail if it's an image
            if matched_item.get('file_type') == 'images' and matched_item.get('thumbnail_url'):
                delete_s3_object(matched_item['thumbnail_url'])

            # Delete from DynamoDB
            table.delete_item(Key={'file_id': matched_item['file_id']})
            deleted_files.append(matched_item['file_id'])

        return {
            'statusCode': 200,
            'body': json.dumps({'deleted_files': deleted_files})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def extract_s3_key(url):
    try:
        parsed = urlparse(url)
        return parsed.path.lstrip('/')
    except Exception:
        return None

def delete_s3_object(url):
    if not url.startswith("s3://") and not url.startswith("https://"):
        return
    if url.startswith("s3://"):
        parts = url[5:].split('/', 1)
    else:
        parsed = urlparse(url)
        parts = [parsed.netloc.split('.')[0], parsed.path.lstrip('/')]
    if len(parts) != 2:
        return
    bucket, key = parts
    try:
        s3.delete_object(Bucket=bucket, Key=key)
    except Exception as e:
        print(f"Error deleting {key} from {bucket}: {e}")
