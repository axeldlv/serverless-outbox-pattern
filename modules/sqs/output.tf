output "sync_queue_fifo_arn" {
  description = "Sync Queue Fifo SQS ARN"
  value       = aws_sqs_queue.sync_queue_fifo.arn
}

output "sync_queue_fifo_url" {
  description = "Sync Queue Fifo SQS URL"
  value       = aws_sqs_queue.sync_queue_fifo.url
}

output "sync_queue_fifo_dlq_arn" {
  description = "Sync Queue Fifo DLQ SQS ARN"
  value       = aws_sqs_queue.sync_queue_dlq_fifo.arn
}

output "sync_queue_fifo_dlq_url" {
  description = "Sync Queue Fifo DLQ SQS URL"
  value       = aws_sqs_queue.sync_queue_dlq_fifo.url
}