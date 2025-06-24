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

orders_table = dynamodb.Table(ORDERS_TABLE)
outbox_table = dynamodb.Table(OUTBOX_TABLE)

logger.info(f"Connected to DynamoDB in region {REGION}")

def insert_order(data, timestamp):
    item = {
        "userId": data["userId"],
        "orderId": data["orderId"],
        "courierId": data.get("courierId"),
        "notificationId": data.get("notificationId"),
        "message": data.get("message"),
        "createdAt": timestamp
    }

    logger.info(f"Inserting order {item['orderId']} into {ORDERS_TABLE}")
    return orders_table.put_item(Item=item)

def insert_outbox(data, timestamp):
    event_id = str(uuid4())
    item = {
        "orderId": data["orderId"],
        "eventId": event_id,
        "eventType": data["eventType"],
        "eventTimestamp": timestamp,
        "status": "PENDING",
        "payload": data
    }

    logger.info(f"Inserting outbox event {event_id} for order {item['orderId']} into {OUTBOX_TABLE}")
    return outbox_table.put_item(Item=item)

def process_record(record):
    body = record.get("body") if isinstance(record, dict) and "body" in record else record
    data = json.loads(body) if isinstance(body, str) else body

    # Validate required fields
    for key in ["orderId", "userId", "eventType"]:
        if key not in data:
            raise ValueError(f"Missing required field: {key}")

    timestamp = data.get("eventTimestamp", datetime.now())

    # Insert into both tables
    insert_order(data, timestamp)
    insert_outbox(data, timestamp)

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