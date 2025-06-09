import os
import boto3
import tempfile
from urllib.parse import unquote_plus
from birds_detection import detect_birds

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')

TABLE_NAME = 'BirdMediaMetadata'

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        file_type = 'image' if key.startswith('images/') else 'video'
        file_name = os.path.basename(key)

        with tempfile.TemporaryDirectory() as tmpdir:
            local_path = os.path.join(tmpdir, file_name)
            s3.download_file(bucket, key, local_path)
            tags = detect_birds(local_path, file_type)

        item = {
            "file_id": {"S": file_name},
            "file_type": {"S": file_type},
            "original_url": {"S": f"s3://{bucket}/{key}"},
            "tags": {"M": {k: {"N": str(v)} for k, v in tags.items()}}
        }

        if file_type == "image":
            thumb_key = f"thumbnails/{file_name.replace('.', '-thumb.')}"
            item["thumbnail_url"] = {"S": f"s3://{bucket}/{thumb_key}"}

        dynamodb.put_item(TableName=TABLE_NAME, Item=item)

    return {"statusCode": 200}