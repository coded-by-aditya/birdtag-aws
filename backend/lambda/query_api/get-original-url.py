import json
import boto3
from boto3.dynamodb.conditions import Attr
import os

# Configuration
TABLE_NAME = 'BirdMediaMetadata'
BUCKET_NAME = 'birdtag-storage-aus-dev'

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # Parse input
        body = json.loads(event['body'])
        thumbnail_url = body.get('thumbnail_url')

        if not thumbnail_url:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing thumbnail_url"})
            }

        # Extract key from thumbnail_url (after the bucket domain)
        key_start = thumbnail_url.find(BUCKET_NAME) + len(BUCKET_NAME) + 1
        thumbnail_key = thumbnail_url[key_start:] if key_start > 0 else None

        if not thumbnail_key:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid thumbnail_url format"})
            }

        # Scan for item with matching thumbnail_url
        response = table.scan(
            FilterExpression=Attr('thumbnail_url').contains(thumbnail_key)
        )

        items = response.get('Items', [])
        if not items:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Thumbnail not found"})
            }

        original_s3_url = items[0].get("original_url", "")
        if not original_s3_url.startswith("s3://"):
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Invalid original_url in DB"})
            }

        # Convert to S3 key
        parts = original_s3_url.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1]

        # Generate pre-signed URL
        presigned_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=3600
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"original_url": presigned_url})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }