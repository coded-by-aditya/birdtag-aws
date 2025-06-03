import boto3
import tempfile
import json
import os
import base64

from birds_detection import image_prediction  # Or video/audio logic if needed

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'BirdMediaMetadata'
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Lambda to find files matching the detected tags of an uploaded media file.
    File is processed on the fly using bird detection model.
    The file is NOT saved in S3 or DynamoDB.

    Expected event (from API Gateway with multipart):
        - body: base64-encoded file content
        - headers['Content-Type']: includes file type

    Returns:
        {
            "detected_tags": [list of tags],
            "matching_files": [list of URLs]
        }
    """
    try:
        print("Event metadata:", json.dumps(event)[:500])  # Truncate if needed

        # Decode base64 body
        if event.get("isBase64Encoded"):
            file_bytes = base64.b64decode(event["body"])
        else:
            raise ValueError("File must be base64 encoded.")

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_file_path = tmp_file.name

        # Run prediction
        result = image_prediction(tmp_file_path)  # Modify if type-checking needed
        tag_counts = result.get("tags", {})
        print("Detected tags:", tag_counts)

        # Extract set of tags for matching
        tag_keys = set(tag_counts.keys())

        # Query DynamoDB
        response = table.scan()
        items = response.get("Items", [])

        matching_files = []
        for item in items:
            existing_tags = item.get("tags", {})
            if tag_keys.issubset(existing_tags.keys()):
                if item['file_type'] == 'image':
                    matching_files.append(convert_s3_to_https(item['thumbnail_url']))
                else:
                    matching_files.append(convert_s3_to_https(item['original_url']))

        return {
            'statusCode': 200,
            'body': json.dumps({
                "detected_tags": list(tag_keys),
                "matching_files": matching_files
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

def convert_s3_to_https(s3_url):
    if s3_url.startswith("s3://"):
        parts = s3_url.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1]
        return f"https://{bucket}.s3.amazonaws.com/{key}"
    return s3_url