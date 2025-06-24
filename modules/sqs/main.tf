resource "aws_sqs_queue" "sync_queue_fifo" {
  name                        = "sync-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.sync_queue_dlq_fifo.arn,
    maxReceiveCount     = 3
  })

  tags = merge(var.common_tags, {
    Name = "sync_queue_fifo"
  })
}

resource "aws_sqs_queue" "sync_queue_dlq_fifo" {
  name                        = "sync-queue-dlq.fifo"
  fifo_queue                  = true
  content_based_deduplication = true

  tags = merge(var.common_tags, {
    Name = "sync_queue_dlq_fifo"
  })
}