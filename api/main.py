from fastapi import FastAPI,HTTPException
from app.storage import Store

app=FastAPI(title='Data Forge',version='0.1.0')
@app.get('/health')
def health(): return {'status':'ok','project':'Data Forge'}
@app.get('/api/snapshot')
def snapshot():
    try:
        store=Store()
        if not store.exists('exports/latest.json'):
            raise HTTPException(404,'No published snapshot. Trigger the Airflow DAG first.')
        pointer=store.json('exports/latest.json')
        return store.json(pointer['key'])
    except HTTPException: raise
    except Exception as exc:
        raise HTTPException(503,'Snapshot storage unavailable') from exc
