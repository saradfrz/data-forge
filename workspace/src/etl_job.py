import boto3
from pyspark.sql import SparkSession

# Retrieve MinIO credentials from the AWS credentials file
session = boto3.Session(profile_name="default")
credentials = session.get_credentials()
access_key = credentials.access_key
secret_key = credentials.secret_key

# Spark session with MinIO configuration
spark = SparkSession.builder \
    .appName("MinIO Glue ETL") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", access_key) \
    .config("spark.hadoop.fs.s3a.secret.key", secret_key) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

# Example: Read data from MinIO
df = spark.read.json("s3a://etl-input/sample.json")
df.show()

# Stop Spark session
spark.stop()
