from fastapi.testclient import TestClient
from api.main import app
from app.storage import Store

def test_no_snapshot_and_published(tmp_path,monkeypatch):
    monkeypatch.setenv('DF_LOCAL_STORE',str(tmp_path))
    c=TestClient(app)
    assert c.get('/health').status_code==200
    assert c.get('/api/snapshot').status_code==404
    store=Store();store.json('exports/x.json',{'synthetic':True,'tables':{}})
    store.json('exports/latest.json',{'key':'exports/x.json'})
    assert c.get('/api/snapshot').json()['synthetic'] is True
