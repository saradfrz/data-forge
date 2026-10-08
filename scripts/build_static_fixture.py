"""Build a labeled preview with the small-data reference implementation.
This does NOT run Kafka, Delta or reconciliation. Cluster publish replaces it only
when a real pipeline run passes reconciliation.
"""
import csv,json,math
from pathlib import Path
from datetime import datetime,timezone
from collections import defaultdict
from decimal import Decimal
from statistics import stdev
from app.domain import validate,event_id,candles,PIPS

def iso(epoch):return datetime.fromtimestamp(epoch,timezone.utc).isoformat()
quotes=[]
for index,row in enumerate(csv.DictReader(open('tests/fixtures/quotes.csv'))):
    q,errors=validate(dict(row,schema_version=1,event_id=event_id('fixture',index),source_order=index))
    if q:quotes.append(q)
tables={x:[] for x in ['gold_candles','gold_spreads','gold_returns','gold_volatility','gold_daily_summary']}
for interval in [1,60,3600]:
 for basis in ['bid','ask','mid']:
  for row in candles(quotes,interval,basis):
   row.update(window_end=iso(row['window_start']+interval),window_start=iso(row['window_start']),interval_seconds=interval,price_basis=basis)
   tables['gold_candles'].append(row)
bins=defaultdict(list)
for q in quotes:bins[(q.instrument,int(q.event_ts.timestamp())//60*60)].append(q)
for (pair,start),values in sorted(bins.items()):
 spreads=[q.ask-q.bid for q in values]
 tables['gold_spreads'].append({'instrument':pair,'window_start':iso(start),'mean_spread_pips':float(sum(spreads)/len(values)/PIPS[pair])})
for pair in sorted({q.instrument for q in quotes}):
 minute=[r for r in tables['gold_candles'] if r['instrument']==pair and r['price_basis']=='mid' and r['interval_seconds']==60]
 previous=None;history=[];rv=[]
 for row in minute:
  eligible=previous and datetime.fromisoformat(row['window_start']).timestamp()-datetime.fromisoformat(previous['window_start']).timestamp()==60
  simple=float(row['close']/previous['close']-1) if eligible else None
  log=math.log(float(row['close']/previous['close'])) if eligible else None
  if log is None:history=[]
  else:history.append(log);rv.append(log)
  tables['gold_returns'].append({'instrument':pair,'sample_end':row['window_end'],'simple_return':simple,'log_return':log})
  tables['gold_volatility'].append({'instrument':pair,'sample_end':row['window_end'],'rolling_log_vol_60m':stdev(history[-60:]) if len(history)>=60 else None})
  previous=row
 selected=sorted([q for q in quotes if q.instrument==pair],key=lambda q:(q.event_ts,q.source_order))
 tables['gold_daily_summary'].append({'instrument':pair,'event_date':'2026-09-15','tick_count':len(selected),
 'mean_spread_pips':float(sum((q.ask-q.bid)/PIPS[pair] for q in selected)/len(selected)),
 'open_close_return':float(selected[-1].mid/selected[0].mid-1),
 'realized_vol_daily':math.sqrt(sum(x*x for x in rv)) if rv else None,'return_coverage':len(rv)/1439,'complete_day':False})
out={'project':'Data Forge','mode':'static reference preview','synthetic':True,'dataset':'fixture-v1','run':'reference-only',
 'generated_at':datetime.now(timezone.utc).isoformat(),'tables':tables,'truncated':{},
 'reconciliation':{'status':'not_run','reason':'Reference preview only; use Airflow for independent batch/Kafka comparison'}}
Path('web/public').mkdir(parents=True,exist_ok=True)
Path('web/public/snapshot.json').write_text(json.dumps(out,default=str,allow_nan=False))
