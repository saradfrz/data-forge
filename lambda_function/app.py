import subprocess
import json

def lambda_handler(event, context):
    
    # Extract file details from event
    record = event['Records'][0]
    bucket_name = record['s3']['bucket']['name']
    file_key = record['s3']['object']['key']
    file_type = record['s3']['object'].get('contentType', '')

    # Validate file type
    if file_type != "application/json":
        return {"statusCode": 400, "body": "Invalid file type"}
    
    # Run the AWS Glue job inside the container
    glue_container = "aws-glue"
    etl_script = "/home/hadoop/workspace/src/etl_job.py"
    minio_s3_path = f"s3://{bucket_name}/{file_key}"

    try:
        cmd = [
            "docker", "exec", glue_container,
            "spark-submit", "--master", "local[*]", etl_script, minio_s3_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        return {"statusCode": 200, "body": f"ETL Job triggered for {file_key}\nOutput: {result.stdout}"}
    except subprocess.CalledProcessError as e:
        return {"statusCode": 500, "body": f"Failed to run ETL Job\nError: {e.stderr}"}
