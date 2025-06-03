import json
import boto3

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'BirdMediaMetadata'
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Lambda function to retrieve the full-size original S3 URL
    based on a thumbnail URL.

    Expects a JSON POST body like:
    {
        "thumbnail_url": "s3://bucket-name/thumbnails/file-thumb.jpg"
    }

    Returns:
        {
            "original_url": "https://bucket-name.s3.amazonaws.com/images/file.jpg"
        }
    """
    try:
        print("Incoming event:", json.dumps(event))
        body = json.loads(event.get('body', '{}'))

        thumb_url = body.get("thumbnail_url")
        if not thumb_url:
            raise ValueError("Missing 'thumbnail_url' in request.")

        # Query DynamoDB for item with matching thumbnail
        response = table.scan()
        items = response.get('Items', [])
        match = next((item for item in items if item.get('thumbnail_url') == thumb_url), None)

        if not match:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Thumbnail not found'})
            }

        # Convert original URL to HTTPS
        https_url = convert_s3_to_https(match['original_url'])

        return {
            'statusCode': 200,
            'body': json.dumps({'original_url': https_url}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    except Exception as e:
        print("Error occurred:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def convert_s3_to_https(s3_url):
    """
    Converts s3://bucket/key to HTTPS access format.
    """
    if s3_url.startswith("s3://"):
        parts = s3_url.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1]
        return f"https://{bucket}.s3.amazonaws.com/{key}"
    return s3_url