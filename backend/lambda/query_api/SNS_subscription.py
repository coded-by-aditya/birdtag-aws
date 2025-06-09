import json
import boto3

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

account_id = "399101466750"
region = "us-east-1"
table = dynamodb.Table('BirdTagSubscriptions')

def lambda_handler(event, context):
    print("=== Incoming Event ===")
    print(json.dumps(event, indent=2))
    print("=== Closing Event ===")
    
    try:
        body = json.loads(event['body'])
        tags = body.get("tags", [])
        email = event["requestContext"]["authorizer"]["jwt"]["claims"]["email"]
    except KeyError as e:
        print("Missing expected field:", str(e))
        return {
            "statusCode": 401,
            "body": json.dumps("Unauthorized: 'claims' missing in requestContext.")
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps("Bad Request: " + str(e))
        }

    if not email or not tags:
        return {"statusCode": 400, "body": json.dumps("Email and tags are required.")}

    # Subscribe to SNS topics
    for tag in tags:
        topic_arn = f"arn:aws:sns:{region}:{account_id}:birdtag-{tag}"
        try:
            sns.subscribe(
                TopicArn=topic_arn,
                Protocol="email",
                Endpoint=email
            )
        except Exception as e:
            print(f"Failed to subscribe to {tag}: {str(e)}")
            continue

    # Save to DynamoDB
    try:
        table.put_item(Item={
            'email': email,
            'tags': tags
        })
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Subscription successful but failed to save to DB: {str(e)}")
        }

    return {
        "statusCode": 200,
        "body": json.dumps("Subscription request sent. Please check your email to confirm.")
    }