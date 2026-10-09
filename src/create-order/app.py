import json
import os
import uuid

import boto3

dynamodb = boto3.resource("dynamodb")
ORDERS_TABLE = os.environ["ORDERS_TABLE"]

def handler(event, context):
    body = json.loads(event["body"])

    customer_id = body.get("customerId")
    items = body.get("items")

    if not customer_id or not items:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "customerId and items are required"
            })
        }

    order_id = str(uuid.uuid4())

    order = {
        "orderId": order_id,
        "customerId": customer_id,
        "items": items,
        "status": "PENDING"
    }

    table = dynamodb.Table(ORDERS_TABLE)
    table.put_item(Item=order)

    return {
        "statusCode": 201,
        "body": json.dumps({
            "message": "Order created successfully",
            "orderId": order_id,
            "status": order["status"]
        })
    }

