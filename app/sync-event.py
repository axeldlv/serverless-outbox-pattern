import boto3
import json
import os
import time
import random
from boto3.dynamodb.types import TypeDeserializer
import logging

# Logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
OUTBOX_TABLE = os.getenv("OUTBOX_TABLE")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")
SQS_ENDPOINT = os.getenv("SQS_ENDPOINT")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
REGION = os.getenv("REGION")

# For localstack only
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# localstack or DynamoDB local
dynamodb = boto3.resource(
    "dynamodb",
    region_name=REGION,
    endpoint_url=DYNAMODB_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# SQS setup
sqs = boto3.client(
    "sqs",
    region_name=REGION,
    endpoint_url=SQS_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)    

deserializer = TypeDeserializer()

def deserialize(dynamo_record):
    return {k: deserializer.deserialize(v) for k, v in dynamo_record.items()}

def send_message_to_sqs_with_retry(queue_url: str, message: dict, attributes: dict, max_retries=3, base_delay=0.5) -> str:
    for attempt in range(max_retries + 1):
        try:
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(message),
                MessageGroupId="outbox-event",
                MessageAttributes=attributes
            )
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            message_id = response.get("MessageId")

            if status_code == 200 and message_id:
                logger.info(f"SQS message sent successfully. MessageId: {message_id}")
                return message_id
            else:
                raise Exception(f"Unexpected SQS response: {response}")

        except Exception as e:
            logger.warning(f"SQS send attempt {attempt + 1} failed: {e}")
            if attempt == max_retries:
                logger.error("Max retries reached. Giving up on message.")
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.3)
            logger.info(f"Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

def lambda_handler(event, context):
    if not event.get("Records"):
        return

    logger.info("Event received: %s", json.dumps(event))

    for record in event['Records']:
        logger.info("Processing record: %s", json.dumps(record))

        if record["eventName"] != "INSERT":
            continue

        try:
            message_record = deserialize(record['dynamodb']['NewImage'])
            status = message_record.get("status")

            if status != "PENDING":
                logger.info(f"Skipping event {message_record.get('eventId')} — already processed.")
                continue

            event_type = message_record.get("eventType")
            order_id = message_record.get("orderId")
            event_id = message_record.get("eventId")
            payload = message_record.get("payload")

            message = {
                "eventType": event_type,
                "data": payload
            }

            # Send to SQS with validation and retry
            message_id = send_message_to_sqs_with_retry(
                queue_url=SQS_QUEUE_URL,
                message=message,
                attributes={
                    'eventType': {
                        'DataType': 'String',
                        'StringValue': event_type
                    }
                }
            )

            # Update DynamoDB status only after successful send
            table = dynamodb.Table(OUTBOX_TABLE)
            table.update_item(
                Key={
                    'orderId': order_id,
                    'eventId': event_id
                },
                UpdateExpression='SET #s = :sent',
                ConditionExpression='#s = :pending',
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={
                    ':sent': 'SENT',
                    ':pending': 'PENDING'
                }
            )

            logger.info(f"Marked event {event_id} as SENT in DynamoDB.")

        except Exception as e:
            logger.error(f"Error processing record: {e}")
            raise

    return {
        "statusCode": 200,
        "body": json.dumps(f"Processed successfully {len(event['Records'])} records.")
    }
