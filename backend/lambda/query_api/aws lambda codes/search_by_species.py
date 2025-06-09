import json
import boto3

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

TABLE_NAME = 'BirdMediaMetadata'
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Lambda function to find files that contain at least one of the specified bird species,
    and return pre-signed URLs for matching items.
    """
    try:
        print("Incoming event:", json.dumps(event))
        body = json.loads(event.get('body', '{}'))

        species_list = body.get("species", [])
        if not isinstance(species_list, list):
            raise ValueError("Field 'species' must be a list.")

        response = table.scan()
        items = response.get('Items', [])

        matching_urls = []

        for item in items:
            tags = item.get('tags', {})

            if any(species in tags and int(tags[species]) >= 1 for species in species_list):
                s3_url = item['thumbnail_url'] if item['file_type'] == 'image' else item['original_url']
                signed_url = generate_presigned_url_from_s3_uri(s3_url)
                if signed_url:
                    matching_urls.append(signed_url)

        return {
            'statusCode': 200,
            'body': json.dumps({'links': matching_urls}),
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

def generate_presigned_url_from_s3_uri(s3_uri):
    """
    Convert s3://bucket/key into a signed HTTPS URL
    """
    try:
        if s3_uri.startswith("s3://"):
            parts = s3_uri.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1]
            return s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=3600  # 1 hour
            )
    except Exception as e:
        print(f"Error signing URL for {s3_uri}: {e}")
    return None