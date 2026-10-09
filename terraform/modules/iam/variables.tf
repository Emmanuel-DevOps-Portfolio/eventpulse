variable "role_name" {
  description = "Name of the IAM role"
  type        = string
}

variable "orders_table_arn" {
  description = "ARN of the DynamoDB orders table"
  type        = string
}