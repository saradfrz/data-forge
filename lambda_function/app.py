import boto3

s3_client = boto3.client("s3", endpoint_url="http://minio:9000")
import json
import os

# MinIO Configuration
BUCKET_NAME = "etl-input"

# AWS Glue Configuration
GLUE_CONTAINER_NAME = "aws-glue-etl"
SPARK_JOB_PATH = "/home/hadoop/workspace/src/etl_job.py"

GLUE_JOB_NAME = "minio-etl-job"  

def lambda_handler(event, context):
    """
    Lambda function triggered by MinIO when a new file is uploaded.
    It starts the AWS Glue ETL job.
    """
    print("Received event:", json.dumps(event, indent=2))

    # Start the Glue job
    response = glue_client.start_job_run(JobName=GLUE_JOB_NAME)

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Glue ETL job triggered successfully!", "JobRunId": response["JobRunId"]})
    }
