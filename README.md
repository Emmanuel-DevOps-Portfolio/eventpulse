# EventPulse: Event Driven Order Processing on AWS

EventPulse is a serverless order processing application built with AWS Lambda, Amazon API Gateway, Amazon DynamoDB, DynamoDB Streams, Amazon SNS, and Terraform.

The project demonstrates how to build an event driven application that accepts orders synchronously and processes them asynchronously, with email notifications published through Amazon SNS.

## Architecture

```text
Client
  |
  v
Amazon API Gateway
  |
  v
Create Order Lambda
  |
  v
Amazon DynamoDB
  |
  | DynamoDB Streams
  v
Process Order Lambda
  |
  v
Amazon SNS
  |
  v
Email Notification
```

### Order processing flow

1. A client submits an order through the API Gateway HTTP API.
2. The Create Order Lambda validates the request and generates an order ID.
3. The order is stored in DynamoDB with an initial status of `PENDING`.
4. DynamoDB Streams captures the new item.
5. The Process Order Lambda receives the stream event and processes new orders.
6. The processing Lambda publishes an order notification to an SNS topic.
7. Amazon SNS delivers the notification to a confirmed email subscription.

## AWS Services

| Service | Purpose |
|---|---|
| Amazon API Gateway | Exposes the order creation endpoint |
| AWS Lambda | Creates and processes orders |
| Amazon DynamoDB | Stores order records |
| DynamoDB Streams | Triggers asynchronous processing |
| Amazon SNS | Publishes order notifications |
| AWS IAM | Controls service permissions |
| Amazon CloudWatch Logs | Captures Lambda execution logs |
| Terraform | Provisions and manages infrastructure |

## API

### Create an order

**Method:** `POST`

**Path:** `/orders`

**Request body:**

```json
{
  "customerId": "customer-001",
  "items": [
    {
      "productId": "product-001",
      "quantity": 2
    }
  ]
}
```

Example successful response:

```json
{
  "message": "Order created successfully",
  "orderId": "generated-order-id",
  "status": "PENDING"
}
```

The order ID is generated for each request.

## Infrastructure as Code

Terraform manages the AWS resources and their configuration.

The development environment is located in:

```text
terraform/
├── environments/
│   └── dev/
└── modules/
```

The configuration includes the order table, Lambda functions, IAM permissions, API Gateway, DynamoDB Streams integration, SNS topic, and email subscription.

Terraform state is stored remotely in Amazon S3, with S3 lockfile-based state locking configured for the project.

### Terraform workflow

From the development environment directory:

```bash
cd terraform/environments/dev
terraform init
terraform fmt
terraform validate
terraform plan
```

Review the plan before applying changes:

```bash
terraform apply
```

For production use, inspect the plan carefully and apply only changes that have been reviewed.

The notification email is supplied through the `notification_email` Terraform variable. Keep local variable files, state files, and saved plans out of source control.

## Testing and Verification

### Local simulation

The repository includes `simulate_eventpulse.py`, which exercises the order creation and processing handlers using mocked DynamoDB and SNS calls.

Run it from the repository root:

```bash
python3 simulate_eventpulse.py
```

The simulation verifies that:

- The Create Order handler returns HTTP 201.
- The order is passed to the mocked DynamoDB write.
- A simulated DynamoDB Streams event reaches the processing handler.
- The processing handler requests an SNS publish.
- The created and processed order IDs match.

The simulation does not write to real AWS resources or send real emails.

### AWS integration test

The deployed workflow was tested using a real API Gateway request.

The test returned HTTP 201 and an order ID. CloudWatch Logs subsequently showed the Process Order Lambda receiving the matching stream event and publishing a message to SNS.

An SNS email notification was also received in the configured inbox.

These checks demonstrate the deployed order processing and notification flow.

## Security and Cost Considerations

- Lambda execution permissions are managed through IAM roles and policies.
- DynamoDB uses on-demand capacity billing.
- The Lambda functions use small memory allocations appropriate for this learning project.
- Terraform state and saved plans may contain sensitive configuration and should be protected.
- SNS email notifications require subscription confirmation before delivery.
- Review AWS resource usage and costs regularly, and remove resources when the project is no longer needed.

## Future Improvements

Potential next steps include:

- Add automated unit tests with a testing framework.
- Improve error handling and retry behavior.
- Design for duplicate event delivery and idempotent processing.
- Add CI/CD automation for infrastructure and application changes.
- Add monitoring, alarms, and operational dashboards.
- Expand order lifecycle management beyond the initial `PENDING` state.

## Technologies

Python · AWS Lambda · Amazon API Gateway · Amazon DynamoDB · DynamoDB Streams · Amazon SNS · AWS IAM · Amazon CloudWatch · Terraform
