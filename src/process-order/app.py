import json
import os
import boto3

sns = boto3.client("sns")
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def handler(event, context):
    for record in event["Records"]:
        if record["eventName"] != "INSERT":
            continue

        order = record["dynamodb"]["NewImage"]

        order_id = order["orderId"]["S"]
        customer_id = order["customerId"]["S"]

        print(json.dumps({
            "message": "New order received for processing",
            "orderId": order_id,
            "customerId": customer_id
        }))

        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="EventPulse: New Order",
            Message=json.dumps({
                "orderId": order_id,
                "customerId": customer_id
            })
        )

        print(json.dumps({
            "message": "SNS notification published",
            "orderId": order_id,
            "messageId": response["MessageId"]
        }))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Stream records processed"
        })
    }