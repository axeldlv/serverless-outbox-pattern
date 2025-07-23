output "lambda_execution_role" {
  description = "ARN of the execution role"
  value       = aws_iam_role.lambda_execution_role.arn
}
