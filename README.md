# Event-Driven Outbox Pattern with AWS, Terraform, and LocalStack

This project demonstrates how to implement the **Outbox Pattern** to guarantee consistency between database writes and event emissions in a distributed microservices architecture. Leveraging AWS services, Terraform infrastructure-as-code, and LocalStack for local testing, this setup ensures reliable, event-driven communication.

You can check technical blog here : [How to Build an Event-Driven Outbox Pattern with AWS, Terraform and LocalStack](https://dev.to/aws-builders/how-to-build-an-event-driven-outbox-pattern-with-aws-terraform-and-localstack-3ie6)

## Prerequisites

- [Terraform](https://www.terraform.io/downloads)
- [LocalStack](https://localstack.cloud/)
- AWS CLI or `awslocal` CLI for LocalStack
- Python 3.12+ (for Lambda code)

## Architecture Overview

- Two DynamoDB tables:
  - `orders` — main business data
  - `orders.outbox` — stores event records with DynamoDB Streams enabled
- Lambda function triggered by DynamoDB Stream on `orders.outbox`
- Lambda publishes events to an SQS FIFO queue

![Architecture Diagram](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/q06mp4kv91v1udphdues.png)

## Features

- Full infrastructure provisioning with Terraform
- AWS services emulated locally using LocalStack
- DynamoDB tables with streams for event tracking
- SQS FIFO queue for reliable message delivery
- Lambda functions to handle:
  - Writing orders and events (outbox-lambda)
  - Processing outbox events and sending to SQS (sync-event lambda)
- Robust error handling and retry logic in Lambda functions