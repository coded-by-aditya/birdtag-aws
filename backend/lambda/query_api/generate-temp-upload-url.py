import json
import boto3
import mimetypes
import os

s3 = boto3.client('s3')

BUCKET_NAME = 'birdtag-storage-aus-dev'

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        filename = body.get('filename')
        folder = body.get('folder', 'temp')  # default to 'temp' if not specified

        if not filename:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing filename'}),
                'headers': {'Access-Control-Allow-Origin': '*'}
            }

        key = f"{folder}/{filename}"
        content_type, _ = mimetypes.guess_type(filename)
        content_type = content_type or 'application/octet-stream'

        url = s3.generate_presigned_url('put_object', {
            'Bucket': BUCKET_NAME,
            'Key': key,
            'ContentType': content_type,
            'Expires': 300  # URL valid for 5 minutes
        })

        return {
            'statusCode': 200,
            'body': json.dumps({'url': url, 'key': key}),
            'headers': {'Access-Control-Allow-Origin': '*'}
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Access-Control-Allow-Origin': '*'}
        }