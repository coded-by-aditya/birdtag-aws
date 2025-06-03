import json
import boto3
from urllib.parse import urlparse

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'BirdMediaMetadata'
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Lambda function to add or remove bird tags from one or more files based on user input.

    Expects JSON body like:
    {
        "url": [ list of S3 https urls ],
        "operation": 1,  # 1 = add, 0 = remove
        "tags": ["crow,1", "pigeon,2"]
    }

    Returns:
        {
            "status": "success",
            "updated_files": [ list of file_ids updated ]
        }
    """
    try:
        print("Incoming event:", json.dumps(event))
        body = json.loads(event.get('body', '{}'))

        urls = body.get("url", [])
        operation = body.get("operation")
        tags_raw = body.get("tags", [])

        if operation not in [0, 1]:
            raise ValueError("Invalid operation. Must be 0 (remove) or 1 (add).")

        # Parse tags into a dict: {"crow": 1, "pigeon": 2}
        tags_to_apply = {}
        for tag_str in tags_raw:
            if ',' in tag_str:
                key, val = tag_str.split(',')
                tags_to_apply[key.strip()] = int(val.strip())

        updated_ids = []

        for url in urls:
            file_id = extract_file_id_from_url(url)
            if not file_id:
                continue

            # Get item
            response = table.get_item(Key={"file_id": file_id})
            item = response.get("Item")
            if not item:
                continue

            # Modify tags
            existing_tags = item.get("tags", {})
            if operation == 1:  # ADD
                for tag, count in tags_to_apply.items():
                    existing_tags[tag] = existing_tags.get(tag, 0) + count
            else:  # REMOVE
                for tag in tags_to_apply:
                    if tag in existing_tags:
                        del existing_tags[tag]

            # Update item in table
            table.update_item(
                Key={"file_id": file_id},
                UpdateExpression="SET tags = :t",
                ExpressionAttributeValues={":t": existing_tags}
            )
            updated_ids.append(file_id)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "updated_files": updated_ids
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def extract_file_id_from_url(url):
    """
    Extracts the file_id from a thumbnail or original HTTPS URL.
    Assumes file_id is the filename at the end of the S3 URL.
    """
    try:
        path = urlparse(url).path
        return os.path.basename(path).replace("-thumb", "").replace(".png", "").replace(".jpg", "").replace(".jpeg", "")
    except Exception:
        return None