variable "lambda_execution_role" {
  description = "ARN of the SQS queue subscribed to SNS"
  type        = string
}

variable "localstack_endpoint" {
  description = "localstack_endpoint"
  type        = string
}

variable "dynamodb_outbox_stream_arn" {
  description = "dynamodb_outbox_stream_arn"
  type        = string
}

variable "dynamodb_outbox_arn" {
  description = "dynamodb_outbox_arn"
  type        = string
}

variable "dynamodb_orders_arn" {
  description = "dynamodb_orders_arn"
  type        = string
}

variable "dynamodb_outbox_name" {
  description = "dynamodb_outbox_name"
  type        = string
}

variable "dynamodb_orders_name" {
  description = "dynamodb_orders_name"
  type        = string
}

variable "common_tags" {
  description = "common_tags"
  type        = map(string)
}

variable "force_lambda_update" {
  description = "Flag to force update of Lambda function"
  type        = bool
  default     = true # Set this to true to force updates
}

variable "sync_queue_url" {
  description = "Sync SQS URL"
  type        = string
}

variable "region" {
  description = "Get region"
  type        = string
}