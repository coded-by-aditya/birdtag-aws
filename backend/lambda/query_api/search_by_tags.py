import json
import boto3
from boto3.dynamodb.conditions import Attr
from decimal import Decimal
from urllib.parse import urlparse

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

table = dynamodb.Table('BirdMediaMetadata')

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        tag_filters = body.get("tags", {})

        if not tag_filters:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'tags' in request body"}),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                }
            }

        response = table.scan()
        items = response.get("Items", [])

        matched_links = []

        for item in items:
            item_tags = item.get("tags", {})
            match = True

            for tag, min_count in tag_filters.items():
                tag_entry = item_tags.get(tag)
                if tag_entry is None or int(tag_entry) < int(min_count):
                    match = False
                    break

            if match:
                file_url = item.get("thumbnail_url") if item.get("file_type") == "image" else item.get("original_url")
                
                if file_url.startswith("s3://"):
                    # Extract key from s3://bucket/key
                    bucket = file_url.split("/")[2]
                    key = "/".join(file_url.split("/")[3:])
                else:
                    parsed = urlparse(file_url)
                    bucket = parsed.netloc.split('.')[0]
                    key = parsed.path.lstrip('/')

                signed_url = s3.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={'Bucket': bucket, 'Key': key},
                    ExpiresIn=3600
                )
                display_url = f"https://{bucket}.s3.amazonaws.com/{key}"

                matched_links.append({
                    "signed_url": signed_url,
                    "display_url": display_url
                })

        return {
            "statusCode": 200,
            "body": json.dumps({"links": matched_links}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

    except Exception as e:
        print("Exception:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({ "error": str(e) }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }