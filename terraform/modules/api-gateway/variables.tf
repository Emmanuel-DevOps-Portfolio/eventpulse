variable "api_name" {
  description = "Name of the API Gateway HTTP API"
  type        = string
}

variable "create_order_lambda_invoke_arn" {
  description = "Invoke ARN of the Create Order Lambda function"
  type        = string
}

variable "create_order_lambda_function_name" {
  description = "Name of the Create Order Lambda function"
  type        = string
}