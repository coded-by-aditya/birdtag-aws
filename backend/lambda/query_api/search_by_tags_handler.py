import json
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdMediaMetadata') 

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        tag_filters = body.get("tags", {})  # Example: { "crow": 2, "pigeon": 1 }

        if not tag_filters:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'tags' in request body"})
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
                if item.get("file_type") == "image":
                    matched_links.append(item.get("thumbnail_url"))
                else:
                    matched_links.append(item.get("original_url"))

        return {
            "statusCode": 200,
            "body": json.dumps({ "links": matched_links }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({ "error": str(e) })
        }