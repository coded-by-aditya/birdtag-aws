import boto3
import json

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

subscription_table = dynamodb.Table('BirdTagSubscriptions')
account_id = "399101466750"
region = "us-east-1"

def lambda_handler(event, context):
    for record in event.get("Records", []):
        if record.get("eventName") not in ["INSERT", "MODIFY"]:
            continue

        new_image = record["dynamodb"].get("NewImage", {})
        if not new_image:
            continue

        # Extract tags
        tags = new_image.get("tags", {}).get("M", {})
        media_url = new_image.get("original_url", {}).get("S", "Unknown")

        # Build a set of detected species
        detected_species = set(tags.keys())

        print(f"Detected species: {detected_species}")
        print(f"Media URL: {media_url}")

        # Scan subscription table
        try:
            response = subscription_table.scan()
            for item in response.get("Items", []):
                email = item["email"]
                subscribed_tags = set(item.get("tags", []))

                # Check for intersection
                if detected_species & subscribed_tags:
                    for tag in detected_species & subscribed_tags:
                        topic_arn = f"arn:aws:sns:{region}:{account_id}:birdtag-{tag}"
                        try:
                            sns.publish(
                                TopicArn=topic_arn,
                                Subject=f"New media with a {tag} detected!",
                                Message=f"A new {tag} was detected! View: {media_url}"
                            )
                            print(f"✅ Notification sent to {email} for {tag}")
                        except Exception as e:
                            print(f"❌ Failed to notify {email} for {tag}: {e}")
        except Exception as e:
            print(f"❌ Failed to scan subscriptions: {e}")