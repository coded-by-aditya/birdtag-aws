import json
import boto3

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        file_ids = body.get("file_ids", [])  # ✅ Expect list of file_ids
        operation = body.get("operation")  # 1 = add, 0 = remove
        tags = body.get("tags", [])

        if not file_ids or operation not in [0, 1] or not tags:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing or invalid input"})
            }

        # Parse tag string to dictionary
        tag_map = {}
        for t in tags:
            name, count = t.split(",")
            tag_map[name.strip()] = int(count.strip())

        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table("BirdMediaMetadata")

        for file_id in file_ids:
            # Get the current item by file_id
            resp = table.get_item(Key={"file_id": file_id})
            item = resp.get("Item")
            if not item:
                continue

            current_tags = item.get("tags", {})
            updated_tags = current_tags.copy()

            if operation == 1:  # Add
                for tag, count in tag_map.items():
                    updated_tags[tag] = updated_tags.get(tag, 0) + count
            else:  # Remove
                for tag, count in tag_map.items():
                    if tag in updated_tags:
                        updated_tags[tag] = max(updated_tags[tag] - count, 0)
                        if updated_tags[tag] == 0:
                            del updated_tags[tag]

            # Update DynamoDB item
            table.update_item(
                Key={"file_id": file_id},
                UpdateExpression="SET tags = :newtags",
                ExpressionAttributeValues={":newtags": updated_tags}
            )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Tag update complete"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }