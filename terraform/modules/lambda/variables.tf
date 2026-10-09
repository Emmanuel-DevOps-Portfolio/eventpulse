variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "handler" {
  description = "The function entrypoint in your code"
  type        = string
}

variable "runtime" {
  description = "The runtime environment for the Lambda function"
  type        = string
}

variable "role_arn" {
  description = "IAM role ARN for the Lambda function"
  type        = string
}

variable "timeout" {
  description = "Function timeout in seconds"
  type        = number
  default     = 30
}

variable "description" {
  description = "Description of the Lambda function"
  type        = string
  default     = ""
}

variable "memory_size" {
  description = "Memory size in MB"
  type        = number
  default     = 128
}

variable "filename" {
  description = "Path to the deployment package (zip file)"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables passed to the Lambda function"
  type        = map(string)
  default     = {}
}