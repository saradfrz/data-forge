import json
from datetime import datetime,timezone
from app.reconcile import KEYS

def publish(spark,store,dataset,run,max_rows):
    check=store.json(f'runs/{run}/reconciliation.json')
    if check['status']!='pass' or check['dataset']!=dataset: raise ValueError('Matching reconciliation required')
    root=f'lake/{dataset}/stream/{run}'
    manifest=store.json(f'manifests/{dataset}.json')
    data={'project':'Data Forge','mode':'historical snapshot','synthetic':manifest['synthetic'],
        'dataset':dataset,'run':run,'generated_at':datetime.now(timezone.utc).isoformat(),
        'reconciliation':check,'tables':{},'table_counts':{},'truncated':{}}
    for name,keys in KEYS.items():
        df=spark.read.format('delta').load(store.uri(root+'/'+name))
        count=df.count();data['table_counts'][name]=count
        # Keep full lake tables; publish a bounded, clearly marked preview.
        rows=df.orderBy(*keys).limit(max_rows).toJSON().collect()
        data['tables'][name]=[json.loads(r) for r in rows]
        data['truncated'][name]=count>max_rows
        df.write.mode('overwrite').parquet(store.uri(f'exports/{run}/parquet/{name}'))
    key=f'exports/{run}/snapshot.json'
    store.json(key,data)
    store.json('exports/latest.json',{'key':key,'generated_at':data['generated_at']})
    return data
