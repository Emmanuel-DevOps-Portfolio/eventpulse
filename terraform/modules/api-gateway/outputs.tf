output "api_id" {
  description = "ID of the EventPulse HTTP API"
  value       = aws_apigatewayv2_api.this.id
}

output "api_endpoint" {
  description = "Base URL of the EventPulse HTTP API"
  value       = aws_apigatewayv2_api.this.api_endpoint
}