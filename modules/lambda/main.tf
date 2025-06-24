resource "aws_lambda_function" "sync_event_lambda" {
  function_name = "syncEventLambda"
  handler       = "sync-event.lambda_handler"
  runtime       = "python3.12"
  filename      = "${path.root}/app/sync-event.zip"

  role = var.lambda_execution_role

  source_code_hash = var.force_lambda_update ? filebase64sha256("${path.root}/app/sync-event.zip") : "" # Forcer la mise à jour du code de la fonction Lambda

  environment {
    variables = {
      DYNAMODB_ENDPOINT     = var.localstack_endpoint
      OUTBOX_TABLE          = var.dynamodb_outbox_name
      SQS_QUEUE_URL         = var.sync_queue_url
      SQS_ENDPOINT          = var.localstack_endpoint
      REGION                = var.region
      AWS_ACCESS_KEY_ID     = "test" # For localstack
      AWS_SECRET_ACCESS_KEY = "test" # For localstack
    }
  }

  tags = merge(var.common_tags, {
    Name = "sync_event_lambda"
  })
}

resource "aws_lambda_function" "outbox_lambda" {
  function_name = "outboxProcessingLambda"
  handler       = "outbox-lambda.lambda_handler"
  runtime       = "python3.12"
  filename      = "${path.root}/app/outbox-lambda.zip"

  role = var.lambda_execution_role

  source_code_hash = var.force_lambda_update ? filebase64sha256("${path.root}/app/outbox-lambda.zip") : "" # Forcer la mise à jour du code de la fonction Lambda

  environment {
    variables = {
      ORDERS_TABLE          = var.dynamodb_orders_name
      OUTBOX_TABLE          = var.dynamodb_outbox_name
      DYNAMODB_ENDPOINT     = var.localstack_endpoint
      REGION                = var.region
      AWS_ACCESS_KEY_ID     = "test" # For localstack
      AWS_SECRET_ACCESS_KEY = "test" # For localstack      
    }
  }

  tags = merge(var.common_tags, {
    Name = "outbox_lambda"
  })
}

resource "aws_lambda_event_source_mapping" "trigger_outbox" {
  event_source_arn  = var.dynamodb_outbox_stream_arn
  function_name     = aws_lambda_function.sync_event_lambda.arn
  starting_position = "LATEST"
  batch_size        = 10

  filter_criteria {
    filter {
      pattern = jsonencode({
        dynamodb = {
          NewImage = {
            status = {
              S = ["PENDING"]
            }
          }
        }
      })
    }
  }

  tags = merge(var.common_tags, {
    Name = "trigger_outbox"
  })
}