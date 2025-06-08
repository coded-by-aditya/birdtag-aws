import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdnetTaggedFiles')

def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        try:
            body = json.loads(event['body'])
            thumbnail_url = body.get('thumbnail_url')
            if not thumbnail_url:
                raise ValueError("Missing thumbnail_url")
        except Exception:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON or missing thumbnail_url'})
            }

    elif event['httpMethod'] == 'GET':
        params = event.get('queryStringParameters', {}) or {}
        thumbnail_url = params.get('thumbnail_url')
        if not thumbnail_url:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing thumbnail_url in query'})
            }

    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method Not Allowed'})
        }

    # Normalize input to match DynamoDB format
    s3_style_thumbnail = convert_https_to_s3(thumbnail_url)

    # Scan the table and find matching thumbnail_url
    try:
        response = table.scan()
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    for item in response['Items']:
        if item.get('thumbnail_url') == s3_style_thumbnail:
            return {
                'statusCode': 200,
                'body': json.dumps({'original_url': convert_to_https(item['original_url'])})
            }

    return {
        'statusCode': 404,
        'body': json.dumps({'error': 'Thumbnail not found'})
    }

def convert_https_to_s3(url):
    if not url.startswith("https://"):
        return url
    try:
        parts = url.replace("https://", "").split(".s3")[0]
        key = url.split(".amazonaws.com/")[1]
        return f"s3://{parts}/{key}"
    except Exception:
        return url  # Fallback, return unchanged if malformed

def convert_to_https(s3_uri):
    if not s3_uri.startswith("s3://"):
        return s3_uri
    parts = s3_uri[5:].split('/', 1)
    bucket = parts[0]
    key = parts[1]
    region = "us-east-1"  # Adjust as needed
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
