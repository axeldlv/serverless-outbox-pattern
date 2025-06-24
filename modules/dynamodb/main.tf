resource "aws_dynamodb_table" "orders" {
  name         = "orders"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "userId"
  range_key = "orderId"

  attribute {
    name = "userId"
    type = "S"
  }

  attribute {
    name = "orderId"
    type = "S"
  }

  tags = merge(var.common_tags, {
    name = "dynamodb_orders_table"
  })
}

resource "aws_dynamodb_table" "outbox" {
  name         = "orders.outbox"
  billing_mode = "PAY_PER_REQUEST"

  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"

  hash_key  = "orderId"
  range_key = "eventId"

  attribute {
    name = "orderId"
    type = "S"
  }

  attribute {
    name = "eventId"
    type = "S"
  }

  tags = merge(var.common_tags, {
    Name = "dynamodb_outbox_table"
  })
}