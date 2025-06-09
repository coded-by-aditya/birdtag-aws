import boto3
import json
from decimal import Decimal
from urllib.parse import urlparse

# Initialize AWS resources
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Your bucket name
BUCKET_NAME = 'birdtag-storage-aus-dev'

# Helper to clean Decimal values from DynamoDB JSON
def clean_decimals(obj):
    if isinstance(obj, list):
        return [clean_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: clean_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    else:
        return obj

# Convert full S3 URL to key and generate presigned URL
def generate_presigned_url(s3_url):
    parsed = urlparse(s3_url)
    key = parsed.path.lstrip("/")  # Remove leading slash
    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': key},
        ExpiresIn=3600
    )

def lambda_handler(event, context):
    table = dynamodb.Table('TempQueryResults')

    file_key = event.get("queryStringParameters", {}).get("key")
    if not file_key:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing key'}),
            'headers': {'Access-Control-Allow-Origin': '*'}
        }

    try:
        result = table.get_item(Key={'file_key': file_key})
        if 'Item' not in result:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Processing'}),
                'headers': {'Access-Control-Allow-Origin': '*'}
            }

        item = clean_decimals(result['Item'])

        # Safely generate presigned URLs only if links exist
        links = item.get('links', [])
        signed_links = [generate_presigned_url(link) for link in links]

        return {
            'statusCode': 200,
            'body': json.dumps({
                'tags': item.get('tags', {}),
                'links': signed_links
            }),
            'headers': {'Access-Control-Allow-Origin': '*'}
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Access-Control-Allow-Origin': '*'}
        }