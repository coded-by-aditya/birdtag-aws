import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdnetTaggedFiles')

def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        try:
            body = json.loads(event['body'])
            if isinstance(body, list):
                species_filter = [s.lower() for s in body]
            elif isinstance(body, dict):
                species_filter = [s.lower() for s in body.keys()]
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid JSON body'})
                }
        except Exception:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON'})
            }

    elif event['httpMethod'] == 'GET':
        params = event.get('queryStringParameters', {}) or {}
        species_filter = [key.lower() for key in params.keys()]

    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method Not Allowed'})
        }

    try:
        response = table.scan()
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    matched_links = []
    for item in response['Items']:
        tags = item.get('tags', {})
        match = all(
            tag in tags and int(tags[tag]) >= 1
            for tag in species_filter
        )

        if match:
            original_url = item.get('original_url')
            if original_url:
                matched_links.append(convert_to_https(original_url))

    return {
        'statusCode': 200,
        'body': json.dumps({'links': matched_links})
    }

def convert_to_https(s3_uri):
    if not s3_uri.startswith("s3://"):
        return s3_uri
    parts = s3_uri[5:].split('/', 1)
    bucket = parts[0]
    key = parts[1]
    region = "us-east-1"  # update if needed
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
