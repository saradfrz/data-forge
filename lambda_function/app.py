def lambda_handler(event, context):
    print("Event received:", event)
    return {"statusCode": 200, "body": "Success"}
