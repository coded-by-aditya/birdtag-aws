import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# DynamoDB table where media metadata is stored
TABLE_NAME = 'BirdMediaMetadata'  # 🔁 Replace this with your actual table name
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    AWS Lambda handler to search for media files based on specified bird species
    and minimum count requirements.

    This function expects a POST request with a JSON body containing bird species
    names as keys and the minimum count of appearances as values. It searches the
    DynamoDB table for media entries that match **all** specified tag requirements
    (logical AND), and returns a list of matching media file URLs.

    Parameters:
        event (dict): AWS Lambda event object (API Gateway proxy format expected)
        context (LambdaContext): AWS Lambda context object

    Returns:
        dict: API Gateway-compatible HTTP response with a JSON body containing:
            {
                "links": [ list of matching S3 URLs as HTTPS ]
            }
    """

    try:
        print("Incoming event:", json.dumps(event))

        # Parse the POST body (example: {"crow": 3, "pigeon": 1})
        body = json.loads(event.get('body', '{}'))

        # Scan the DynamoDB table to get all items
        response = table.scan()
        items = response.get('Items', [])

        matching_urls = []

        for item in items:
            tags = item.get('tags', {})
            match = True  # Flag for AND logic

            # Check if each tag in request is present with >= requested count
            for bird, min_count in body.items():
                if int(tags.get(bird, 0)) < int(min_count):
                    match = False
                    break  # No need to check further if one fails

            if match:
                # Decide which URL to return based on file type
                if item['file_type'] == 'image':
                    matching_urls.append(convert_s3_to_https(item['thumbnail_url']))
                else:
                    matching_urls.append(convert_s3_to_https(item['original_url']))

        # Return a JSON list of links
        return {
            'statusCode': 200,
            'body': json.dumps({'links': matching_urls}),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # CORS support
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
    Helper function to convert s3://bucket/key format into
    https://bucket.s3.amazonaws.com/key format.

    Parameters:
        s3_url (str): S3-style URL (e.g., s3://my-bucket/path/to/file.jpg)

    Returns:
        str: HTTPS version of the URL
    """
    if s3_url.startswith("s3://"):
        parts = s3_url.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1]
        return f"https://{bucket}.s3.amazonaws.com/{key}"
    return s3_url