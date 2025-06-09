import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("BirdMediaMetadata")
s3 = boto3.client("s3")

BUCKET_NAME = "birdtag-storage-aus-dev"

# Helper to handle Decimal to float/int
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

def generate_presigned_url(s3_url):
    if not s3_url or not s3_url.startswith("s3://"):
        return None
    parts = s3_url.replace("s3://", "").split("/", 1)
    if len(parts) != 2:
        return None
    bucket, key = parts
    try:
        return s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=3600  # 1 hour
        )
    except Exception as e:
        print(f"Error generating pre-signed URL for {s3_url}: {e}")
        return None

def lambda_handler(event, context):
    try:
        response = table.scan()
        items = response.get("Items", [])

        # Add pre-signed URLs for each item
        for item in items:
            if "original_url" in item:
                item["original_url"] = generate_presigned_url(item["original_url"])
            if "thumbnail_url" in item:
                item["thumbnail_url"] = generate_presigned_url(item["thumbnail_url"])

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(items, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }