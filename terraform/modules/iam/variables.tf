variable "role_name" {
  description = "Name of the IAM role"
  type        = string
}

variable "orders_table_arn" {
  description = "ARN of the DynamoDB orders table"
  type        = string
}

variable "enable_dynamodb_put_item" {
  description = "Whether this role can write items to the orders table"
  type        = bool
  default     = true
}