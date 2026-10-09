output "api_id" {
  description = "ID of the EventPulse HTTP API"
  value       = module.api_gateway.api_id
}

output "api_endpoint" {
  description = "Base URL of the EventPulse HTTP API"
  value       = module.api_gateway.api_endpoint
}