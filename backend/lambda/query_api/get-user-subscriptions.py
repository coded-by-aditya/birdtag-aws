import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('BirdTagSubscriptions')

def lambda_handler(event, context):
    # 🔍 Debug log the incoming event
    print("=== Incoming Event ===")
    print(json.dumps(event, indent=2))

    try:
        # ✅ Correct path to get email from JWT claims in HTTP API
        email = event['requestContext']['authorizer']['jwt']['claims']['email']
    except KeyError as e:
        print("❌ KeyError while extracting email:", str(e))
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Unauthorized: 'email' claim missing"})
        }

    try:
        response = table.get_item(Key={"email": email})
        item = response.get("Item", {})
        tags = item.get("tags", [])
        print(f"✅ Found subscription for {email}: {tags}")
    except Exception as e:
        print("❌ Error fetching from DynamoDB:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    return {
        "statusCode": 200,
        "body": json.dumps({"email": email, "tags": tags})
    }