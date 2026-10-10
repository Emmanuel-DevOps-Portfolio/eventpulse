terraform {
  backend "s3" {
    bucket       = "eventpulse-terraform-state-941377151096"
    key          = "eventpulse/dev/terraform.tfstate"
    region       = "eu-west-1"
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}

module "orders_table" {
  source = "../../modules/dynamodb"

  table_name = "eventpulse-dev-orders"
}

module "create_order_iam" {
  source = "../../modules/iam"

  role_name        = "eventpulse-dev-create-order-role"
  orders_table_arn = module.orders_table.table_arn
}

module "create_order_lambda" {
  source = "../../modules/lambda"

  function_name = "eventpulse-dev-create-order"
  description   = "Creates customer orders and saves them to DynamoDB"
  handler       = "app.handler"
  runtime       = "python3.12"
  role_arn      = module.create_order_iam.lambda_execution_role_arn
  timeout       = 10
  memory_size   = 128

  filename = "${path.root}/../../../dist/create-order.zip"

  environment_variables = {
    ORDERS_TABLE = module.orders_table.table_name
  }
}

module "process_order_lambda" {
  source = "../../modules/lambda"

  function_name = "eventpulse-dev-process-order"
  description   = "Processes newly created orders from DynamoDB Streams"
  handler       = "app.handler"
  runtime       = "python3.12"

  role_arn    = module.process_order_iam.lambda_execution_role_arn
  timeout     = 10
  memory_size = 128

  filename = "${path.root}/../../../dist/process-order.zip"
}

resource "aws_lambda_event_source_mapping" "process_orders" {
  event_source_arn  = module.orders_table.stream_arn
  function_name     = module.process_order_lambda.function_name
  starting_position = "LATEST"
  batch_size        = 10
  enabled           = true

  filter_criteria {
    filter {
      pattern = jsonencode({
        eventName = ["INSERT"]
      })
    }
  }
}

module "api_gateway" {
  source = "../../modules/api-gateway"

  api_name                          = "eventpulse-dev-api"
  create_order_lambda_invoke_arn    = module.create_order_lambda.invoke_arn
  create_order_lambda_function_name = module.create_order_lambda.function_name
}

module "process_order_iam" {
  source = "../../modules/iam"

  role_name                = "eventpulse-dev-process-order-role"
  orders_table_arn         = module.orders_table.table_arn
  enable_dynamodb_put_item = false
}

resource "aws_iam_role_policy" "process_order_stream_read" {
  name = "eventpulse-dev-process-order-stream-read"
  role = module.process_order_iam.lambda_execution_role_name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:DescribeStream",
          "dynamodb:GetRecords",
          "dynamodb:GetShardIterator"
        ]
        Resource = module.orders_table.stream_arn
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:ListStreams"]
        Resource = "*"
      }
    ]
  })
}