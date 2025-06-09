import json
import boto3

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("BirdMediaMetadata")

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        file_ids = body.get("file_ids", [])  # ✅ Expect list of file_ids

        if not file_ids:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No file_ids provided"})
            }

        deleted_items = []

        for file_id in file_ids:
            # Get item to find associated S3 URLs
            resp = table.get_item(Key={"file_id": file_id})
            item = resp.get("Item")
            if not item:
                continue

            # Delete original and thumbnail URLs from S3
            for s3_url in [item.get("original_url"), item.get("thumbnail_url")]:
                if s3_url and s3_url.startswith("s3://"):
                    parts = s3_url.replace("s3://", "").split("/", 1)
                    if len(parts) == 2:
                        bucket, key = parts
                        try:
                            s3.delete_object(Bucket=bucket, Key=key)
                        except Exception as e:
                            print(f"Failed to delete from S3: {s3_url}, error: {e}")

            # Delete item from DynamoDB
            table.delete_item(Key={"file_id": file_id})
            deleted_items.append(file_id)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Files deleted",
                "deleted": deleted_items
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }