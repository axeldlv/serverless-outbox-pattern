provider "aws" {
  region = local.region

  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true

  endpoints {
    cloudformation = local.localstack_endpoint
    cloudwatch     = local.localstack_endpoint
    dynamodb       = local.localstack_endpoint
    iam            = local.localstack_endpoint
    lambda         = local.localstack_endpoint
    s3             = local.localstack_s3_endpoint
    sqs            = local.localstack_endpoint
  }
}

module "iam" {
  source      = "./modules/iam"
  common_tags = local.common_tags
}

module "dynamodb" {
  source      = "./modules/dynamodb"
  common_tags = local.common_tags
}

module "lambda" {
  source                     = "./modules/lambda"
  lambda_execution_role      = module.iam.lambda_execution_role
  localstack_endpoint        = local.localstack_endpoint
  dynamodb_outbox_stream_arn = module.dynamodb.dynamodb_outbox_stream_arn
  dynamodb_outbox_arn        = module.dynamodb.dynamodb_outbox_arn
  dynamodb_orders_arn        = module.dynamodb.dynamodb_orders_arn
  dynamodb_outbox_name       = module.dynamodb.dynamodb_outbox_name
  dynamodb_orders_name       = module.dynamodb.dynamodb_orders_name
  sync_queue_url             = module.sqs.sync_queue_fifo_url
  common_tags                = local.common_tags
  region                     = local.region
}

module "sqs" {
  source      = "./modules/sqs"
  common_tags = local.common_tags
}