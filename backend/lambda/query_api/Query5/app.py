import json
import boto3
from urllib.parse import urlparse

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdnetTaggedFiles')

def lambda_handler(event, context):
    try:
        # Handle raw test payloads or API Gateway proxy requests
        if 'body' in event and isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            body = event  # Assume already parsed JSON (e.g. from test)

        urls = body.get('url', [])
        operation = body.get('operation')
        tag_entries = body.get('tags', [])

        if not isinstance(urls, list) or not isinstance(tag_entries, list) or operation not in (0, 1):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid input structure'})
            }

        # Parse tags into a dict
        tag_map = {}
        for tag_entry in tag_entries:
            if ',' not in tag_entry:
                continue
            species, count = tag_entry.split(',')
            tag_map[species.strip().lower()] = int(count)

        updated = []

        for url in urls:
            s3_key = extract_s3_key(url)
            if not s3_key:
                continue

            file_id = s3_key.split('/')[-1]

            # Fetch item
            item = table.get_item(Key={'file_id': file_id}).get('Item')
            if not item:
                continue

            tags = item.get('tags', {})

            if operation == 1:  # Add or replace tags
                for tag, count in tag_map.items():
                    tags[tag] = count
            else:  # Remove tags
                for tag in tag_map:
                    tags.pop(tag, None)

            # Save back to DynamoDB
            table.update_item(
                Key={'file_id': file_id},
                UpdateExpression='SET tags = :t',
                ExpressionAttributeValues={':t': tags}
            )
            updated.append(file_id)

        return {
            'statusCode': 200,
            'body': json.dumps({'updated_files': updated})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def extract_s3_key(url):
    try:
        parsed = urlparse(url)
        return parsed.path.lstrip('/')
    except Exception:
        return None
