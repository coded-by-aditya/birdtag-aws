import json
import boto3
from boto3.dynamodb.conditions import Attr

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

        # Connect to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('BirdMediaMetadata')

        # Scan for the matching thumbnail_url
        response = table.scan(
            FilterExpression=Attr('thumbnail_url').eq(thumbnail_url)
        )

        items = response.get('Items', [])
        if not items:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Thumbnail not found"})
            }

        # Return original URL
        original_url = items[0].get("original_url", "")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"original_url": original_url})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }