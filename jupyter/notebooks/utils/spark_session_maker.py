from pyspark.sql import SparkSession
import os
import logging

from dotenv import load_dotenv
from pathlib import Path

# Specify the custom path to your .env file
env_path = Path('/home/jovyan/work/.env')
load_dotenv(dotenv_path=env_path)

class SparkSessionMaker:
    def __init__(self, app_name: str, region: str = "us-east-1"):
        """
        Initialize the ETL job with the given parameters.
        """
        self.app_name = app_name
        self.region = region
        self._get_credentials_from_env()
        self.spark = self._create_spark_session()
        
    def _get_credentials_from_env(self):
        self.access_key = os.environ.get('MINIO_ACCESS_KEY')
        self.secret_key = os.environ.get('MINIO_SECRET_KEY')
        self.minio_endpoint = os.environ.get('MINIO_ENDPOINT')
        self.spark_master = os.environ.get('SPARK_MASTER')
    
    def _create_spark_session(self) -> SparkSession:
        """
        Create and return a Spark session configured to use MinIO via the S3A connector.
        """
        spark = SparkSession.builder \
            .appName(self.app_name) \
            .master(self.spark_master) \
            .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1") \
            .config("spark.hadoop.fs.s3a.endpoint", self.minio_endpoint) \
            .config("spark.hadoop.fs.s3a.access.key", self.access_key) \
            .config("spark.hadoop.fs.s3a.secret.key", self.secret_key) \
            .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
            .getOrCreate()
        
        
        return spark



