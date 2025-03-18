import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType
import logging

# Configure logging for the pipeline
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ExchangeRatesPipeline")

class ExchangeRatesProcessor:
    """
    A class to process exchange rates data from a JSON file.
    It reads the file from an S3-compatible storage (MinIO),
    calculates the mean of exchange rates, and writes the result
    into a Postgres database.
    """
    def __init__(self, input_path: str, postgres_url: str, table_name: str, postgres_properties: dict):
        """
        Initializes the ExchangeRatesProcessor with configuration parameters.
        
        Parameters:
            input_path (str): S3 path to the input JSON file (e.g., s3a://etl-input/filename.json).
            postgres_url (str): JDBC URL for the Postgres database.
            table_name (str): The target table name in the Postgres database.
            postgres_properties (dict): Properties including user, password, and JDBC driver.
        """
        self.input_path = input_path
        self.postgres_url = postgres_url
        self.table_name = table_name
        self.postgres_properties = postgres_properties
        
        # Create a Spark session with necessary configuration for S3 (MinIO) access
        logger.info("Initializing Spark session with S3 (MinIO) configuration.")
        self.spark = SparkSession.builder \
            .appName("ExchangeRatesProcessing") \
            .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
            .config("spark.hadoop.fs.s3a.access.key", "minio") \
            .config("spark.hadoop.fs.s3a.secret.key", "minio123") \
            .config("spark.hadoop.fs.s3a.path.style.access", "true") \
            .getOrCreate()
        logger.info("Spark session created successfully.")

    def read_data(self):
        """
        Reads the JSON file from the specified input path.
        
        Returns:
            DataFrame: A Spark DataFrame representing the JSON data.
        """
        try:
            logger.info(f"Attempting to read JSON data from {self.input_path}.")
            df = self.spark.read.json(self.input_path)
            logger.info(f"Data read successfully from {self.input_path}.")
            return df
        except Exception as e:
            logger.error("Error reading data from %s: %s", self.input_path, e)
            raise

    def compute_means(self, df):
        """
        Processes the DataFrame to compute the mean exchange rates.
        
        The JSON is expected to have a nested 'data' field with keys:
        'dolar_compra', 'dolar_venta', 'real_compra', 'real_venta', 'euro_compra', and 'euro_venta'.
        
        Returns:
            DataFrame: A DataFrame with calculated mean values.
        """
        try:
            logger.info("Starting computation of mean exchange rates.")
            # Flatten the nested 'data' field
            rates_df = df.select("institution", "`updated at`", "data.*")
            logger.info("Data flattened successfully.")
            
            # Convert string values to double for computation
            logger.info("Casting currency fields to double.")
            rates_df = rates_df.withColumn("dolar_compra", F.col("dolar_compra").cast(DoubleType())) \
                               .withColumn("dolar_venta", F.col("dolar_venta").cast(DoubleType())) \
                               .withColumn("real_compra", F.col("real_compra").cast(DoubleType())) \
                               .withColumn("real_venta", F.col("real_venta").cast(DoubleType())) \
                               .withColumn("euro_compra", F.col("euro_compra").cast(DoubleType())) \
                               .withColumn("euro_venta", F.col("euro_venta").cast(DoubleType()))
            logger.info("Currency fields casted successfully.")

            # Calculate the mean for each currency
            logger.info("Calculating mean values for currencies.")
            rates_df = rates_df.withColumn("dolar_mean", (F.col("dolar_compra") + F.col("dolar_venta")) / 2) \
                               .withColumn("real_mean", (F.col("real_compra") + F.col("real_venta")) / 2) \
                               .withColumn("euro_mean", (F.col("euro_compra") + F.col("euro_venta")) / 2)
            logger.info("Mean exchange rates calculated successfully.")
            
            return rates_df
        except Exception as e:
            logger.error("Error during computation of mean exchange rates: %s", e)
            raise

    def write_to_postgres(self, df):
        """
        Writes the processed DataFrame to a Postgres database table.
        
        Parameters:
            df (DataFrame): The DataFrame with computed means.
        """
        try:
            logger.info("Writing processed data to Postgres database at %s", self.postgres_url)
            df.write.jdbc(url=self.postgres_url, table=self.table_name, mode="append", properties=self.postgres_properties)
            logger.info("Data written to Postgres successfully.")
        except Exception as e:
            logger.error("Error writing data to Postgres: %s", e)
            raise

    def process(self):
        """
        Executes the complete ETL process: read, compute, and write.
        """
        logger.info("ETL process started.")
        df = self.read_data()
        logger.info("Data successfully read. Proceeding with computation of means.")
        df_means = self.compute_means(df)
        logger.info("Computation complete. Proceeding with writing to Postgres.")
        self.write_to_postgres(df_means)
        logger.info("ETL process completed successfully.")

def main():
    """
    Main entry point for the ETL job. Expects command-line arguments for configuration.
    
    Usage:
        spark-submit etl_job.py <input_path> <postgres_url> <table_name> <postgres_user> <postgres_password>
    """
    if len(sys.argv) < 6:
        logger.error("Invalid number of arguments. Expected usage: spark-submit etl_job.py <input_path> <postgres_url> <table_name> <postgres_user> <postgres_password>")
        print("Usage: spark-submit etl_job.py <input_path> <postgres_url> <table_name> <postgres_user> <postgres_password>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    postgres_url = sys.argv[2]
    table_name = sys.argv[3]
    postgres_user = sys.argv[4]
    postgres_password = sys.argv[5]
    
    logger.info("Initializing ExchangeRatesProcessor with parameters:")
    logger.info("Input Path: %s", input_path)
    logger.info("Postgres URL: %s", postgres_url)
    logger.info("Table Name: %s", table_name)
    
    postgres_properties = {
        "user": postgres_user,
        "password": postgres_password,
        "driver": "org.postgresql.Driver"
    }
    
    processor = ExchangeRatesProcessor(input_path, postgres_url, table_name, postgres_properties)
    try:
        processor.process()
    except Exception as e:
        logger.error("ETL process failed: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
