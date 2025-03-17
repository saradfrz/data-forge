from minio import Minio
from minio.error import S3Error

# MinIO client setup
minio_client = Minio(
    'localhost:9000',  # No path should be included here
    access_key='minio',
    secret_key='minio123',
    secure=False
)


# Bucket name and file details
bucket_name = 'etl-input'
file_path = '/root/projects/data-forge/playground/input/exchange_rate__cambio_principal_20241206064911.json'
object_name = 'exchange_rate__cambio_principal_20241206064911.json'

# Check if the bucket exists, if not, create it
try:
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
    else:
        print(f"Bucket '{bucket_name}' already exists.")
    
    # Upload the file
    minio_client.fput_object(bucket_name, object_name, file_path)
    print(f"File '{file_path}' uploaded to '{bucket_name}/{object_name}'.")

except S3Error as e:
    print(f"Error: {e}")
