import json
import boto3

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("BirdMediaMetadata")

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        urls = body.get("urls", [])

        if not urls:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No URLs provided"})
            }

        deleted_items = []

        for url in urls:
            # Convert S3 URL to bucket and key
            if not url.startswith("s3://"):
                continue
            parts = url.replace("s3://", "").split("/", 1)
            if len(parts) != 2:
                continue
            bucket, key = parts

            # Delete from S3
            try:
                s3.delete_object(Bucket=bucket, Key=key)
            except Exception as e:
                print(f"Failed to delete from S3: {url}, error: {e}")

            # Delete from DynamoDB if this is original file or thumbnail
            scan_result = table.scan()
            for item in scan_result.get("Items", []):
                if url in [item.get("original_url"), item.get("thumbnail_url")]:
                    table.delete_item(Key={"file_id": item["file_id"]})
                    deleted_items.append(item["file_id"])

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