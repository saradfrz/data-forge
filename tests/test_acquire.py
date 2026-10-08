import json
from pathlib import Path
import pytest
from app.acquire import ingest,events
from app.storage import Store
from app.domain import validate

def test_idempotent_import(tmp_path,monkeypatch):
    monkeypatch.setenv('DF_LOCAL_STORE',str(tmp_path/'store'))
    store=Store();store.ensure()
    fixture=Path('tests/fixtures/quotes.csv')
    a=ingest(store,fixture,'x',synthetic=True);b=ingest(store,fixture,'x',synthetic=True)
    assert a==b
    with pytest.raises(ValueError): ingest(store,fixture,'x',mapping={'instrument':'GBPUSD'},synthetic=True)
    with pytest.raises(ValueError): ingest(store,fixture,'x',synthetic=False)
    rows=list(events(store,'x'))
    assert len(rows)==a['record_count']
    assert len({e['event_id'] for e in rows})==len(rows)
    assert sum(bool(validate(e)[1]) for e in rows)==2
    changed=tmp_path/'changed.csv';changed.write_text(fixture.read_text()+'EURUSD,bad,1,2,,\n')
    with pytest.raises(ValueError): ingest(store,changed,'x')
    with pytest.raises(ValueError):store.path('../escape')
