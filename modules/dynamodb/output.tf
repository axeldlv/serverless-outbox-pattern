output "dynamodb_outbox_stream_arn" {
  description = "ARN of the dynamodb stream outbox"
  value       = aws_dynamodb_table.outbox.stream_arn
}

output "dynamodb_outbox_arn" {
  description = "ARN of the dynamodb outbox"
  value       = aws_dynamodb_table.outbox.arn
}

output "dynamodb_outbox_name" {
  description = "Name of the dynamodb outbox"
  value       = aws_dynamodb_table.outbox.name
}

output "dynamodb_orders_arn" {
  description = "ARN of the dynamodb orders"
  value       = aws_dynamodb_table.orders.arn
}

output "dynamodb_orders_name" {
  description = "Name of the dynamodb orders"
  value       = aws_dynamodb_table.orders.name
}