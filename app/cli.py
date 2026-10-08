import argparse
import json
import re
from app.storage import Store

class Application:
    def __init__(self,config,logger): self.config,self.logger=config,logger
    def run(self):
        p=argparse.ArgumentParser(description='Data Forge pipeline commands')
        p.add_argument('command',choices=['ingest','batch','replay','stream','gold','reconcile','publish','pause','resume'])
        p.add_argument('--dataset',default='fixture-v1');p.add_argument('--run',default='demo-v1')
        p.add_argument('--csv',default='tests/fixtures/quotes.csv');p.add_argument('--mapping')
        p.add_argument('--synthetic',action='store_true')
        p.add_argument('--path',choices=['batch','stream'],default='batch')
        p.add_argument('--speed',type=float,default=10);p.add_argument('--rate',type=float,default=100)
        a=p.parse_args()
        for name in [a.dataset,a.run]:
            if not re.fullmatch('[a-zA-Z0-9_-]{1,80}',name): raise ValueError('Invalid dataset/run identifier')
        store=Store(self.config.storage.bucket);store.ensure()
        if a.command=='ingest':
            from app.acquire import ingest
            mapping=json.load(open(a.mapping)) if a.mapping else None
            result=ingest(store,a.csv,a.dataset,mapping,a.synthetic)
        elif a.command=='replay':
            from app.replay import replay
            result=replay(store,a.dataset,a.run,a.speed,a.rate)
        elif a.command in ['pause','resume']:
            result={'paused':a.command=='pause'};store.json(f'runs/{a.run}/control.json',result)
        else:
            from app.pipelines.session import spark_session
            from app.pipelines import lakehouse,gold
            from app.reconcile import reconcile
            from app.publish import publish
            spark=spark_session(self.config)
            try:
                root=f'lake/{a.dataset}/batch' if a.path=='batch' else f'lake/{a.dataset}/stream/{a.run}'
                if a.command=='batch': result=lakehouse.batch(spark,store,a.dataset)
                elif a.command=='stream': result=lakehouse.stream(spark,store,a.dataset,a.run,self.config.pipeline.max_offsets_per_trigger)
                elif a.command=='gold': gold.build(spark,store,root);result={'root':root}
                elif a.command=='reconcile': result=reconcile(spark,store,a.dataset,a.run)
                elif a.command=='publish':
                    result=publish(spark,store,a.dataset,a.run,self.config.pipeline.max_export_rows)
                    result={k:v for k,v in result.items() if k!='tables'}
            finally: spark.stop()
        self.logger.info('Command %s finished',a.command)
        print(json.dumps(result,default=str))
