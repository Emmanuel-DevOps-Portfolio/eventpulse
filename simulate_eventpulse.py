
import json
import os
from importlib.util import module_from_spec, spec_from_file_location
from unittest.mock import MagicMock, patch


# Configure the environment required when loading the Create Order handler.
os.environ["ORDERS_TABLE"] = "eventpulse-dev-orders"
os.environ["SNS_TOPIC_ARN"] = (
    "arn:aws:sns:eu-west-1:000000000000:simulated-topic"
)


def load_handler(name, path):
    """Load a Lambda handler directly from its Python file."""
    spec = spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load handler from {path}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def to_stream_attribute(value):
    """Convert Python values into DynamoDB Streams attribute format."""
    if isinstance(value, str):
        return {"S": value}

    if isinstance(value, bool):
        return {"BOOL": value}

    if isinstance(value, (int, float)):
        return {"N": str(value)}

    if value is None:
        return {"NULL": True}

    if isinstance(value, list):
        return {
            "L": [to_stream_attribute(item) for item in value]
        }

    if isinstance(value, dict):
        return {
            "M": {
                key: to_stream_attribute(item)
                for key, item in value.items()
            }
        }

    raise TypeError(f"Unsupported value type: {type(value)}")


def main():
    # Load both Lambda handlers.
    create_order = load_handler(
        "create_order",
        "src/create-order/app.py"
    )

    process_order = load_handler(
        "process_order",
        "src/process-order/app.py"
    )

    # Simulate an API Gateway POST /orders request.
    api_event = {
        "body": json.dumps({
            "customerId": "customer-test-001",
            "items": [
                {
                    "productId": "product-001",
                    "quantity": 2
                }
            ]
        })
    }

    # Mock DynamoDB so no real AWS write occurs.
    mock_table = MagicMock()

    with patch.object(
        create_order.dynamodb,
        "Table",
        return_value=mock_table
    ):
        print("\n=== STEP 1: CREATE ORDER ===")

        create_response = create_order.handler(api_event, None)

    print("HTTP status:", create_response["statusCode"])
    print("Response:", create_response["body"])

    assert create_response["statusCode"] == 201

    response_body = json.loads(create_response["body"])

    # Verify that the handler attempted to save the order.
    mock_table.put_item.assert_called_once()
    saved_order = mock_table.put_item.call_args.kwargs["Item"]

    assert saved_order["orderId"] == response_body["orderId"]

    print("\nSimulated DynamoDB item:")
    print(json.dumps(saved_order, indent=2))

    # Simulate the DynamoDB Streams INSERT event.
    stream_event = {
        "Records": [
            {
                "eventName": "INSERT",
                "dynamodb": {
                    "NewImage": {
                        key: to_stream_attribute(value)
                        for key, value in saved_order.items()
                    }
                }
            }
        ]
    }

    # Mock SNS so no real notification is published.
    mock_sns = MagicMock()
    mock_sns.publish.return_value = {
        "MessageId": "simulated-message-id"
    }

    print("\n=== STEP 2: PROCESS ORDER ===")

    with patch.object(process_order, "sns", mock_sns):
        process_response = process_order.handler(
            stream_event,
            None
        )

    print("Handler response:", process_response)

    assert process_response["statusCode"] == 200
    mock_sns.publish.assert_called_once()

    publish_args = mock_sns.publish.call_args.kwargs

    notification = json.loads(publish_args["Message"])

    assert notification["orderId"] == saved_order["orderId"]
    assert notification["customerId"] == saved_order["customerId"]

    print("\nSimulated SNS publish:")
    print("Subject:", publish_args["Subject"])
    print("Topic ARN:", publish_args["TopicArn"])
    print("Message:", json.dumps(notification))
    print("Message ID:", mock_sns.publish.return_value["MessageId"])

    # Summarize the local simulation.
    print("\n=== VERIFICATION ===")
    print("Created order ID:", response_body["orderId"])
    print("Processed order ID:", saved_order["orderId"])
    print(
        "Order IDs match:",
        response_body["orderId"] == saved_order["orderId"]
    )
    print("DynamoDB write mocked:", mock_table.put_item.called)
    print("SNS publish mocked:", mock_sns.publish.called)
    print("\nLocal simulation completed successfully.")


if __name__ == "__main__":
    main()
