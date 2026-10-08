import csv
import io
import json
from pathlib import Path
from datetime import datetime,timezone
from app.domain import digest,event_id

def ingest(store, csv_path, dataset, mapping=None, synthetic=False):
    """One canonical CSV per dataset. A changed file requires a new dataset ID."""
    raw=Path(csv_path).read_bytes(); sha=digest(raw)
    mapping=mapping or {}
    key=f'manifests/{dataset}.json'
    if store.exists(key):
        old=store.json(key)
        if old['sha256']!=sha or old['mapping']!=mapping or old['synthetic']!=synthetic: raise ValueError('Dataset immutable: use a new dataset ID')
        return old
    store.put(f'raw/{dataset}/{sha}.csv',raw)
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')),delimiter=mapping.get('delimiter',','))
    fields=mapping.get('fields',{})
    parts=[];chunk=[];count=0
    for index,row in enumerate(reader):
        def value(name): return row.get(fields.get(name,name),'')
        t=value('event_ts')
        if mapping.get('timestamp_format'):
            # Explicit timezone required; no implicit local interpretation.
            try: t=datetime.strptime(t,mapping['timestamp_format']).isoformat()
            except ValueError: pass  # preserve malformed value for quarantine
        e={'schema_version':1,'dataset_id':dataset,'event_id':event_id(sha,index),
           'source_file_id':sha,'source_row_index':index,'source_order':index,
           'instrument':value('instrument') or mapping.get('instrument',''),
           'event_ts':t,'bid':value('bid'),'ask':value('ask'),
           'bid_volume_source':value('bid_volume_source'),'ask_volume_source':value('ask_volume_source'),
           'volume_unit':mapping.get('volume_unit','unverified'),'raw_record':row}
        chunk.append(json.dumps(e,separators=(',',':')));count+=1
        if len(chunk)>=10000:
            part=f'events/{dataset}/part-{len(parts):06d}.jsonl'
            store.put(part,'\n'.join(chunk)+'\n');parts.append(part);chunk=[]
    if chunk:
        part=f'events/{dataset}/part-{len(parts):06d}.jsonl'
        store.put(part,'\n'.join(chunk)+'\n');parts.append(part)
    if not count: raise ValueError('CSV has no data records')
    manifest={'dataset_id':dataset,'sha256':sha,'record_count':count,'parts':parts,
              'synthetic':synthetic,'acquired_at':datetime.now(timezone.utc).isoformat(),
              'mapping':mapping,'original_filename':Path(csv_path).name}
    store.json(key,manifest)
    return manifest

def events(store,dataset):
    for part in store.json(f'manifests/{dataset}.json')['parts']:
        for line in store.get(part).decode().splitlines():
            yield json.loads(line)
