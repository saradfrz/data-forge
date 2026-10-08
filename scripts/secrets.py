"""Generate local lab credentials once. Never print their values."""
import base64
import secrets
import os
from pathlib import Path
p=Path('.env')
if p.exists():
    existing=dict(line.split('=',1) for line in p.read_text().splitlines() if '=' in line and not line.startswith('#'))
    required=['MINIO_ROOT_USER','MINIO_ROOT_PASSWORD','POSTGRES_PASSWORD','AIRFLOW_DB_URL','AIRFLOW_FERNET_KEY','AIRFLOW_JWT_SECRET']
    if any(not existing.get(key) for key in required):
        raise SystemExit('Existing .env is incomplete; fill every field in .env.example before continuing.')
    print('Reusing existing .env; no credentials overwritten.')
else:
    password=secrets.token_hex(24)
    values={'MINIO_ROOT_USER':'forgeadmin','MINIO_ROOT_PASSWORD':secrets.token_hex(24),
        'POSTGRES_PASSWORD':password,'AIRFLOW_DB_URL':f'postgresql+psycopg2://airflow:{password}@postgres:5432/airflow',
        'AIRFLOW_FERNET_KEY':base64.urlsafe_b64encode(os.urandom(32)).decode(),
        'AIRFLOW_JWT_SECRET':secrets.token_hex(32)}
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:
        f.write(''.join(f'{k}={v}\n' for k,v in values.items()))
    print('Created private .env for this local lab.')
