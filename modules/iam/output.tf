output "lambda_execution_role" {
  description = "ARN of the monitoring SQS queue"
  value       = aws_iam_role.lambda_execution_role.arn
}