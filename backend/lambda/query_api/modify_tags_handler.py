import json
import boto3
from boto3.dynamodb.conditions import Attr

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        urls = body.get("url", [])
        operation = body.get("operation")  # 1 = add, 0 = remove
        tags = body.get("tags", [])

        if not urls or operation not in [0, 1] or not tags:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing or invalid input"})
            }

        tag_map = {}
        for t in tags:
            name, count = t.split(",")
            tag_map[name.strip()] = int(count.strip())

        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table("BirdMediaMetadata")

        for url in urls:
            scan_resp = table.scan(
                FilterExpression=Attr("thumbnail_url").eq(url)
            )
            items = scan_resp.get("Items", [])
            if not items:
                continue

            item = items[0]
            current_tags = item.get("tags", {})
            updated_tags = current_tags.copy()

            if operation == 1:
                for tag, count in tag_map.items():
                    updated_tags[tag] = updated_tags.get(tag, 0) + count
            else:
                for tag, count in tag_map.items():
                    if tag in updated_tags:
                        updated_tags[tag] = max(updated_tags[tag] - count, 0)
                        if updated_tags[tag] == 0:
                            del updated_tags[tag]

            table.update_item(
                Key={"file_id": item["file_id"]},
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