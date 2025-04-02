import logging
import os
from logging.handlers import RotatingFileHandler
import requests
from datetime import datetime as dt
import json
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
from io import BytesIO

dotenv_path = "/robots/.env"
if not os.path.isfile(dotenv_path):
    logging.error(f"Warning: Could not find environment file at {dotenv_path}")
else:
    load_dotenv(dotenv_path, override=True)


class RobotsUtils():        
    
    def _config_logger(self, log_folder):

        os.makedirs(log_folder, exist_ok=True)

        log_file = os.path.join(log_folder, 'exchange_rate.log')

        logger = logging.getLogger('ExchangeRateLogger')
        logger.setLevel(logging.DEBUG)

        # Create a rotating file handler
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
        file_handler.setLevel(logging.DEBUG)

        # Create a console handler for debugging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create a log formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _get_html(self):
        try:
            logger = self.logger
            url = self.url
            
            response = requests.get(url, verify=False)
            response.raise_for_status() 
            logger.info(f"Successfully fetched data from {url}")
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            exit()
            
    def _save_data_to_json(self, exchange_rate, filename):
        try:
            logger = self.logger
            date_hash = dt.now().strftime('%Y%m%d%H%M%S')
            
            os.makedirs('output', exist_ok=True)
            with open(f'output/{filename}_{date_hash}.json', 'w') as f:
                json.dump(exchange_rate, f, indent=4)
            logger.info(f"Exchange rate data successfully saved to '{filename}_{date_hash}.json'")
        except Exception as e:
            logger.error(f"Error saving exchange rate data: {e}")
            
    def _save_data_to_minio(self, exchange_rate, filename):
        try:
            logger = self.logger

            minio_client = Minio(
                os.getenv('MINIO_SERVER'),
                access_key=os.getenv('MINIO_ACCESS_KEY'),
                secret_key=os.getenv('MINIO_SECRET_KEY'),
                secure=False
            )

            bucket_name = os.getenv('MINIO_BUCKET')
            date_hash = dt.now().strftime('%Y%m%d%H%M%S')
            object_name = f'{filename}_{date_hash}.json'
            
            bucket_name = os.getenv('MINIO_BUCKET')

            # Check if bucket exists; if not, create it
            found = minio_client.bucket_exists(bucket_name)
            logging.info(f"Bucket {bucket_name} exists: {found}")
            if not found:
                minio_client.make_bucket(bucket_name)

            # Convert the exchange rate data to JSON bytes
            json_data = json.dumps(exchange_rate).encode('utf-8')
            data_stream = BytesIO(json_data)
            data_length = len(json_data)

            # Use put_object to upload the data
            minio_client.put_object(bucket_name, object_name, data_stream, data_length)
            logger.info(f"Exchange rate data successfully saved to {bucket_name}/{object_name}")
        except S3Error as e:
            logger.error(f"Error: {e}")

