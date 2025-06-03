import json
import boto3
from urllib.parse import urlparse
import os

# Initialize AWS clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'BirdMediaMetadata'
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Lambda function to delete media files and their thumbnails (if image),
    and remove corresponding metadata from DynamoDB.

    Expects a JSON body:
    {
        "urls": [ list of HTTPS S3 URLs ]
    }

    Returns:
        {
            "deleted": [list of successfully deleted file_ids],
            "errors": [list of any failed deletions]
        }
    """
    try:
        print("Incoming event:", json.dumps(event))
        body = json.loads(event.get('body', '{}'))
        urls = body.get("urls", [])

        deleted_ids = []
        errors = []

        for url in urls:
            bucket, key = parse_s3_url(url)
            if not bucket or not key:
                errors.append(f"Invalid URL: {url}")
                continue

            file_id = extract_file_id_from_key(key)
            if not file_id:
                errors.append(f"Could not extract file_id from: {url}")
                continue

            # Attempt to delete file from S3
            try:
                s3.delete_object(Bucket=bucket, Key=key)
            except Exception as s3e:
                errors.append(f"Failed S3 delete: {url} → {str(s3e)}")

            # Attempt to remove from DynamoDB
            try:
                table.delete_item(Key={"file_id": file_id})
                deleted_ids.append(file_id)
            except Exception as dbe:
                errors.append(f"Failed DB delete: {file_id} → {str(dbe)}")

            # If it's a thumbnail, also try to delete the full-size image
            if 'thumbnails/' in key:
                original_key = key.replace('thumbnails/', '').replace('-thumb', '')
                try:
                    s3.delete_object(Bucket=bucket, Key=original_key)
                except Exception as e:
                    errors.append(f"Failed full image delete: {original_key} → {str(e)}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "deleted": deleted_ids,
                "errors": errors
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

    except Exception as e:
        print("Unhandled error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({'error': str(e)})
        }

def parse_s3_url(https_url):
    """
    Converts HTTPS S3 URL to bucket and key
    """
    parsed = urlparse(https_url)
    host_parts = parsed.netloc.split('.')
    if len(host_parts) < 1:
        return None, None
    bucket = host_parts[0]
    key = parsed.path.lstrip('/')
    return bucket, key

def extract_file_id_from_key(s3_key):
    """
    Extracts file_id from S3 key assuming filename is the ID (without -thumb or extension)
    """
    base = os.path.basename(s3_key)
    file_id = base.replace("-thumb", "").split('.')[0]
    return file_id