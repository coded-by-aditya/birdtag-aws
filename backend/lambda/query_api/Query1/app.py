import json
import boto3
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdnetTaggedFiles')

# Change this to your region
REGION = 'us-east-1'

def s3_to_https(s3_url):
    # Converts s3://bucket/key to https://bucket.s3.region.amazonaws.com/key
    if not s3_url.startswith("s3://"):
        return s3_url
    parts = s3_url.replace("s3://", "").split("/", 1)
    bucket = parts[0]
    key = parts[1]
    return f"https://{bucket}.s3.{REGION}.amazonaws.com/{key}"

def lambda_handler(event, context):
    # Extract tag filters
    if event['httpMethod'] == 'POST':
        try:
            tag_filters = json.loads(event['body'])
        except Exception as e:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON'})
            }
    elif event['httpMethod'] == 'GET':
        params = event.get('queryStringParameters', {}) or {}
        tag_filters = {}
        for key, value in params.items():
            if key.startswith('tag'):
                idx = key[3:]
                count_key = f"count{idx}"
                tag = value.lower()
                count = int(params.get(count_key, 1))
                tag_filters[tag] = count
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method Not Allowed'})
        }

    # Scan the table
    try:
        response = table.scan()
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    results = []
    for item in response['Items']:
        tags = item.get('tags', {})
        match = True
        for tag, min_count in tag_filters.items():
            tag_data = tags.get(tag)
            try:
                if tag_data is None or int(tag_data) < min_count:
                    match = False
                    break
            except Exception:
                match = False
                break

        if match:
            if item['file_type'] == 'images' and 'thumbnail_url' in item:
                results.append(s3_to_https(item['thumbnail_url']))
            elif item['file_type'] == 'videos':
                results.append(s3_to_https(item['original_url']))

    return {
        'statusCode': 200,
        'body': json.dumps({'links': results})
    }
