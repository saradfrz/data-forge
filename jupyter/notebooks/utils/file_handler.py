class FileHandler():
    def __init__(self, spark_session):
        self.spark = spark_session.spark

    def open_csv(self, bucket_name, file_name):
        """
        Returns a spark dataframe with the csv data
        """
        file_path = f"s3a://{bucket_name}/{file_name}"
        return self.spark.read.option("header", "True").option("inferSchema", "true").csv(file_path)
    
    def open_txt(self, bucket_name, file_name):
        """
        Returns a spark dataframe with the txt data
        """
        file_path = f"s3a://{bucket_name}/{file_name}"
        return self.spark.read.text(file_path)