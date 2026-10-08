"""S3 storage with a filesystem implementation for dependency-free checks."""
import json
import os
from pathlib import Path

class Store:
    def __init__(self, bucket='data-forge'):
        self.bucket=bucket
        self.local=os.getenv('DF_LOCAL_STORE')
        if not self.local:
            import boto3
            from botocore.config import Config
            self.client=boto3.client('s3',endpoint_url=os.environ['S3_ENDPOINT'],
                aws_access_key_id=os.environ['MINIO_ROOT_USER'],
                aws_secret_access_key=os.environ['MINIO_ROOT_PASSWORD'],region_name='us-east-1',
                config=Config(signature_version='s3v4',s3={'addressing_style':'path'}))
    def ensure(self):
        if self.local:
            Path(self.local).mkdir(parents=True,exist_ok=True)
        else:
            from botocore.exceptions import ClientError
            try: self.client.head_bucket(Bucket=self.bucket)
            except ClientError as exc:
                if exc.response['Error']['Code'] not in ['404','NoSuchBucket']: raise
                self.client.create_bucket(Bucket=self.bucket)
    def path(self,key):
        root=Path(self.local).resolve()
        p=(root/key).resolve()
        if not p.is_relative_to(root): raise ValueError('Unsafe object key')
        return p
    def exists(self,key):
        if self.local: return self.path(key).is_file()
        from botocore.exceptions import ClientError
        try: self.client.head_object(Bucket=self.bucket,Key=key); return True
        except ClientError as exc:
            if exc.response['Error']['Code'] in ['404','NoSuchKey']: return False
            raise
    def put(self,key,body):
        if isinstance(body,str): body=body.encode()
        if self.local:
            p=self.path(key);p.parent.mkdir(parents=True,exist_ok=True)
            tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_bytes(body);tmp.replace(p)
        else: self.client.put_object(Bucket=self.bucket,Key=key,Body=body)
    def get(self,key):
        if self.local: return self.path(key).read_bytes()
        return self.client.get_object(Bucket=self.bucket,Key=key)['Body'].read()
    def json(self,key,value=None):
        if value is None: return json.loads(self.get(key))
        self.put(key,json.dumps(value,sort_keys=True,default=str,allow_nan=False))
    def uri(self,key):
        return str(self.path(key)) if self.local else f's3a://{self.bucket}/{key}'
    def list(self,prefix):
        if self.local:
            return sorted(str(p.relative_to(Path(self.local).resolve())) for p in self.path(prefix).rglob('*') if p.is_file())
        pages=self.client.get_paginator('list_objects_v2').paginate(Bucket=self.bucket,Prefix=prefix)
        return sorted(o['Key'] for page in pages for o in page.get('Contents',[]))
