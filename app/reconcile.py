from decimal import Decimal
import math

KEYS={
 'gold_candles':['instrument','window_start','interval_seconds','price_basis'],
 'gold_spreads':['instrument','window_start'],
 'gold_returns':['instrument','sample_end'],
 'gold_volatility':['instrument','sample_end'],
 'gold_daily_summary':['instrument','event_date']}

def equal(a,b):
    if a is None or b is None: return a is None and b is None
    if isinstance(a,Decimal) or isinstance(b,Decimal): return Decimal(a)==Decimal(b)
    if isinstance(a,float) or isinstance(b,float):
        return math.isfinite(float(a)) and math.isfinite(float(b)) and math.isclose(float(a),float(b),abs_tol=1e-12,rel_tol=1e-9)
    return a==b

def compare_rows(left,right,keys):
    def index(rows):
        d={tuple(r[k] for k in keys):r for r in rows}
        if len(d)!=len(rows): raise ValueError('Duplicate reconciliation keys')
        return d
    l,r=index(left),index(right); diff=[]
    for key in sorted(l.keys()|r.keys()):
        if key not in l or key not in r: diff.append({'key':key,'reason':'missing_or_extra'});continue
        for field in l[key].keys()|r[key].keys():
            if field not in l[key] or field not in r[key] or not equal(l[key].get(field),r[key].get(field)):
                diff.append({'key':key,'field':field,'batch':l[key].get(field),'stream':r[key].get(field)})
    return diff

def reconcile(spark,store,dataset,run):
    """Distributed equality joins; only bounded mismatch examples reach driver."""
    from pyspark.sql import functions as F
    from pyspark.sql.types import FloatType,DoubleType
    b=f'lake/{dataset}/batch';s=f'lake/{dataset}/stream/{run}'
    manifest=store.json(f'manifests/{dataset}.json')
    reports=[]
    for table,keys in {'silver':['event_id'],**KEYS}.items():
        left=spark.read.format('delta').load(store.uri(b+'/'+table))
        right=spark.read.format('delta').load(store.uri(s+'/'+table))
        columns=[c for c in left.columns if c not in ['raw','ingested_at']]
        left=left.select(columns);right=right.select(columns)
        # Join on explicit key, not row position. Null-safe field comparisons.
        joined=left.alias('b').join(right.alias('s'),keys,'full')
        same=F.lit(True)
        for field in left.schema:
            if field.name in keys: continue
            x,y=F.col('b.'+field.name),F.col('s.'+field.name)
            if isinstance(field.dataType,(FloatType,DoubleType)):
                ok=(x.isNull()&y.isNull()) | (x.isNotNull()&y.isNotNull()&
                    (F.abs(x-y)<=F.lit(1e-12)+F.lit(1e-9)*F.greatest(F.abs(x),F.abs(y))))
            else: ok=x.eqNullSafe(y)
            same=same&F.coalesce(ok,F.lit(False))
        missing=left.select(keys).join(right.select(keys),keys,'left_anti').count()
        extra=right.select(keys).join(left.select(keys),keys,'left_anti').count()
        mismatches=joined.filter(~same)
        count=mismatches.count()
        reports.append({'table':table,'missing':missing,'extra':extra,'mismatched_rows':count,
            'examples':[r.asDict() for r in mismatches.select(keys).limit(20).collect()]})
    counts={}
    for label,root in [('batch',b),('stream',s)]:
        valid=spark.read.format('delta').load(store.uri(root+'/silver')).count()
        quarantine=spark.read.format('delta').load(store.uri(root+'/quarantine'))
        rejected=quarantine.select(F.get_json_object('raw','$.event_id').alias('id')).distinct().count()
        counts[label]={'accepted':valid,'quarantined_unique':rejected}
        if valid+rejected!=manifest['record_count']: raise RuntimeError('Source accounting failed')
    passed=all(not (x['missing'] or x['extra'] or x['mismatched_rows']) for x in reports)
    result={'status':'pass' if passed else 'fail','dataset':dataset,'run':run,'tables':reports,'counts':counts}
    store.json(f'runs/{run}/reconciliation.json',result)
    if not passed: raise RuntimeError('Reconciliation failed; inspect report')
    return result
