import json

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

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Stream records processed"
        })
    }