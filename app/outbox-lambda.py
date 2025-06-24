import json
import logging
import boto3
import os
from datetime import datetime
from uuid import uuid4
from botocore.exceptions import ClientError

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Environment variables
ORDERS_TABLE = os.getenv("ORDERS_TABLE")
OUTBOX_TABLE = os.getenv("OUTBOX_TABLE")
REGION = os.getenv("REGION")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")

if not all([ORDERS_TABLE, OUTBOX_TABLE, REGION]):
    raise EnvironmentError("Missing required environment variables.")


# For localstack only
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

dynamodb = boto3.resource(
    "dynamodb",
    region_name=REGION,
    endpoint_url=DYNAMODB_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
dynamodb_client = boto3.client('dynamodb')

orders_table = dynamodb.Table(ORDERS_TABLE)
outbox_table = dynamodb.Table(OUTBOX_TABLE)

logger.info(f"Connected to DynamoDB in region {REGION}")

def insert_order_and_outbox(data, timestamp):
    response = dynamodb_client.transact_write_items(
        TransactItems=[
            {
                'Put': {
                    'TableName': ORDERS_TABLE,
                    'Item': {
                        'userId': {'S': data["userId"]},
                        'orderId': {'S': data["orderId"]},
                        'courierId': {'S': data.get("courierId")},
                        'notificationId': {'S': data.get("notificationId")},
                        'message': {'S': data.get("message")},
                        'createdAt': {'S': str(timestamp)}

                    }
                }
            },
            {
                'Put': {
                    'TableName': OUTBOX_TABLE,
                    'Item': {
                        'orderId': {'S': data["orderId"]},
                        'eventId': {'S': str(uuid4())},
                        'eventType': {'S': data["eventType"]},
                        'eventTimestamp': {'S': str(timestamp)},
                        'status': {'S': "PENDING"},
                        'payload': {'S': json.dumps(data)}
                    }
                }
            }
        ]
    )
    return response


def process_record(record):
    body = record.get("body") if isinstance(record, dict) and "body" in record else record
    data = json.loads(body) if isinstance(body, str) else body

    # Validate required fields
    for key in ["orderId", "userId", "eventType"]:
        if key not in data:
            raise ValueError(f"Missing required field: {key}")

    timestamp = data.get("eventTimestamp", datetime.now())

    logger.info(f"Inserting order and outbox for orderId={data['orderId']}")
    # Insert into both tables in the same transaction
    insert_order_and_outbox(data, timestamp)

    logger.info(f"Successfully processed orderId={data['orderId']}")

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    records = event.get("Records", [event])

    for record in records:
        try:
            process_record(record)
        except ClientError as e:
            logger.error(f"AWS ClientError: {e.response['Error']['Message']}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": e.response['Error']['Message']})
            }
        except Exception as e:
            logger.error(f"General error: {str(e)}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Processed successfully"})
    }