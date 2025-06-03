import json
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# DynamoDB table name (replace with your actual table name)
TABLE_NAME = 'BirdMediaMetadata'
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Lambda function to find all files containing at least one of the specified bird species.
    
    This function expects a JSON POST body like:
    {
        "species": ["crow", "myna"]
    }

    It scans the database and returns media files (thumbnails for images, direct links for others)
    where the 'tags' field contains at least one of the specified species.

    Parameters:
        event (dict): AWS Lambda event object
        context (LambdaContext): AWS Lambda context

    Returns:
        dict: HTTP response with list of matching file URLs
    """
    try:
        print("Incoming event:", json.dumps(event))
        body = json.loads(event.get('body', '{}'))

        # Extract the species list
        species_list = body.get("species", [])
        if not isinstance(species_list, list):
            raise ValueError("Field 'species' must be a list.")

        # Fetch all items from DynamoDB
        response = table.scan()
        items = response.get('Items', [])

        matching_urls = []

        for item in items:
            tags = item.get('tags', {})

            # Check for presence of any species in the tag list
            if any(species in tags and int(tags[species]) >= 1 for species in species_list):
                if item['file_type'] == 'image':
                    matching_urls.append(convert_s3_to_https(item['thumbnail_url']))
                else:
                    matching_urls.append(convert_s3_to_https(item['original_url']))

        return {
            'statusCode': 200,
            'body': json.dumps({'links': matching_urls}),
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
    Converts an S3-style URL (s3://bucket/key) to HTTPS format.

    Parameters:
        s3_url (str): The S3-style URL

    Returns:
        str: HTTPS URL to access the file
    """
    if s3_url.startswith("s3://"):
        parts = s3_url.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1]
        return f"https://{bucket}.s3.amazonaws.com/{key}"
    return s3_url