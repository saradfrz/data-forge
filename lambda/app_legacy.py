import os
import json
import subprocess
import logging
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()  # This looks for a .env file in the current working directory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LambdaSparkTrigger")

class LambdaSparkTrigger:
    """
    Processes a MinIO event and triggers a Spark job.

    It performs the following steps:
      - Extracts event details (bucket, key, content type) from the event payload.
      - Validates that the file is of type application/json.
      - Constructs the S3 input path and invokes a Spark job via spark-submit.
    """

    def __init__(self, spark_master_url: str, etl_script_path: str, 
                 postgres_url: str, table_name: str, 
                 postgres_user: str, postgres_password: str):
        self.spark_master_url = spark_master_url
        self.etl_script_path = etl_script_path
        self.postgres_url = postgres_url
        self.table_name = table_name
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password

    def extract_event_details(self, event: dict):
        try:
            record = event['Records'][0]
            bucket_name = record['s3']['bucket']['name']
            file_key = record['s3']['object']['key']
            file_type = record['s3']['object'].get('contentType', '')
            logger.info(f"Extracted event: bucket={bucket_name}, key={file_key}, type={file_type}")
            return bucket_name, file_key, file_type
        except Exception as e:
            logger.error("Error extracting event details: %s", e)
            raise

    def validate_file(self, file_type: str):
        if file_type != "application/json":
            logger.error("Invalid file type: %s", file_type)
            raise ValueError("Invalid file type. Only application/json is supported.")

    def trigger_spark_job(self, bucket_name: str, file_key: str) -> str:
        # Construct the S3 input path for Spark
        input_path = f"s3a://{bucket_name}/{file_key}"
        # Build the spark-submit command with all required parameters
        command = [
            "spark-submit",
            "--master", self.spark_master_url,
            self.etl_script_path,
            input_path,
            self.postgres_url,
            self.table_name,
            self.postgres_user,
            self.postgres_password
        ]
        logger.info("Executing Spark job with command: %s", " ".join(command))
        
        # Execute the Spark job
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Spark job submission failed: %s", result.stderr)
            raise RuntimeError(f"Spark job failed: {result.stderr}")
        logger.info("Spark job executed successfully: %s", result.stdout)
        return result.stdout

def lambda_handler(event, context):
    """
    AWS Lambda entry point that processes the event and triggers the Spark job.
    
    Expects the following environment variables (loaded from the .env file):
      - SPARK_MASTER_URL: URL for the Spark master.
      - ETL_SCRIPT_PATH: Path to the Spark ETL job script.
      - POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD: Postgres credentials.
      - TABLE_NAME: The target Postgres table name.
    """
    # Retrieve Spark-related configuration
    spark_master_url = os.environ.get("SPARK_MASTER_URL", "spark://spark-master:7077")
    etl_script_path = os.environ.get("ETL_SCRIPT_PATH", "/opt/bitnami/spark/workspace/etl_job.py")
    
    # Build the Postgres JDBC URL using the .env credentials
    postgres_host = os.environ.get("POSTGRES_HOST")
    postgres_port = os.environ.get("POSTGRES_PORT")
    postgres_db = os.environ.get("POSTGRES_DB")
    postgres_url = f"jdbc:postgresql://{postgres_host}:{postgres_port}/{postgres_db}"
    
    table_name = os.environ.get("TABLE_NAME", "exchange_rates")
    postgres_user = os.environ.get("POSTGRES_USER")
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    
    trigger = LambdaSparkTrigger(
        spark_master_url, etl_script_path,
        postgres_url, table_name,
        postgres_user, postgres_password
    )
    
    try:
        # Extract event details
        bucket_name, file_key, file_type = trigger.extract_event_details(event)
        # Validate the file type
        trigger.validate_file(file_type)
    except Exception as e:
        error_message = f"Invalid event data: {str(e)}"
        logger.error(error_message)
        return {"statusCode": 400, "body": error_message}
    
    try:
        # Trigger the Spark job
        logger.info("Triggering Spark job...")
        output = trigger.trigger_spark_job(bucket_name, file_key)
        success_message = f"Spark job submitted successfully: {output}"
        logger.info(success_message)
        return {"statusCode": 200, "body": success_message}
    except Exception as e:
        error_message = f"Spark job submission failed: {str(e)}"
        logger.error(error_message)
        return {"statusCode": 500, "body": error_message}
