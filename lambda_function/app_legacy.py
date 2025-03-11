import boto3
import json
import os

# MinIO Configuration (bucket name is coming from the event)
MINIO_BUCKET_NAME = "etl-input"  # This can be overridden by the event data if needed

# AWS Glue Configuration
GLUE_CONTAINER_NAME = "aws-glue"
SPARK_JOB_PATH = "/home/hadoop/workspace/src/etl_job.py"
GLUE_JOB_NAME = "minio-etl-job"

# MinIO S3 Client (Ensure proper credentials if MinIO requires them)
s3_client = boto3.client(
    "s3",
    endpoint_url="http://minio:9000",  # Your MinIO endpoint
    aws_access_key_id=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),  # MinIO credentials
    aws_secret_access_key=os.getenv("MINIO_SECRET_KEY", "minioadmin")
)

# AWS Glue Client (Ensure correct AWS credentials)
glue_client = boto3.client("glue")

def lambda_handler(event, context):
    """
    Lambda function triggered by MinIO when a new file is uploaded.
    It starts the AWS Glue ETL job.
    """
    print("Received event:", json.dumps(event, indent=2))

    # Extracting the bucket and object name from the event.
    try:
        # Assuming the event is from MinIO and has the structure as follows
        # { "Records": [{ "s3": { "bucket": { "name": "<bucket_name>" }, "object": { "key": "<object_key>" } } }] }
        record = event.get("Records", [])[0]  # Get the first record in case of multiple

        bucket_name = record.get("s3", {}).get("bucket", {}).get("name")
        object_key = record.get("s3", {}).get("object", {}).get("key")

        # Log the bucket and object details
        print(f"File uploaded: {object_key} in bucket: {bucket_name}")

        if bucket_name != MINIO_BUCKET_NAME:
            raise ValueError(f"Received event from unexpected bucket: {bucket_name}")

        # Now, start the AWS Glue job
        response = glue_client.start_job_run(JobName=GLUE_JOB_NAME, Arguments={
            "--bucket_name": bucket_name,
            "--object_key": object_key,
            "--spark_job_path": SPARK_JOB_PATH
        })

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Glue ETL job triggered successfully!",
                "JobRunId": response["JobRunId"]
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
