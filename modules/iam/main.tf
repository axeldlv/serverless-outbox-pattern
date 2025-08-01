resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda-execution-role"

  assume_role_policy = <<EOF
    {
      "Version": "2012-10-17",
      "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
        "Service": "lambda.amazonaws.com"
        },
      "Effect": "Allow",
      "Sid": ""
      }]
    }
    EOF

  tags = merge(var.common_tags, {
    Name = "lambda-execution-role"
  })
}