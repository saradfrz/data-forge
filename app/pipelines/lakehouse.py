"""Single writer per dataset/path/run. Durable Bronze precedes validation."""
import json
import os
from app.domain import normalized_json

def merge(df,path,keys):
    from delta.tables import DeltaTable
    from pyspark.sql import functions as F
    df=df.dropDuplicates(keys)
    if DeltaTable.isDeltaTable(df.sparkSession,path):
        (DeltaTable.forPath(df.sparkSession,path).alias('t').merge(df.alias('s'),
         ' AND '.join(f't.{k} = s.{k}' for k in keys)).whenNotMatchedInsertAll().execute())
    else: df.write.format('delta').mode('errorifexists').save(path)

def consume_frame(frame,store,root):
    from pyspark.sql import functions as F
    normalized='event_id string, instrument string, event_ts string, source_order long, bid string, ask string, reasons array<string>, quality_flags array<string>, bid_volume_source double, ask_volume_source double, volume_unit string'
    merge(frame,store.uri(root+'/bronze'),['delivery_id'])
    decode=F.udf(normalized_json,'string')
    expanded=(frame.withColumn('q',F.from_json(decode('raw'),normalized)))
    rejected=expanded.filter(F.size('q.reasons')>0).select('delivery_id','raw','ingested_at',F.col('q.reasons').alias('reasons'))
    merge(rejected,store.uri(root+'/quarantine'),['delivery_id'])
    accepted=(expanded.filter(F.size('q.reasons')==0)
        .select('q.*','raw','ingested_at')
        .withColumn('event_ts',F.to_timestamp('event_ts'))
        .withColumn('bid',F.col('bid').cast('decimal(20,10)'))
        .withColumn('ask',F.col('ask').cast('decimal(20,10)'))
        .withColumn('mid',((F.col('bid')+F.col('ask'))/2).cast('decimal(21,11)'))
        .withColumn('spread_abs',(F.col('ask')-F.col('bid')).cast('decimal(20,10)')))
    # Identity derives from immutable source SHA+row. Transport envelope differs by replay.
    merge(accepted,store.uri(root+'/silver'),['event_id'])

def batch(spark,store,dataset):
    from pyspark.sql import functions as F
    manifest=store.json(f'manifests/{dataset}.json')
    frame=spark.read.text([store.uri(k) for k in manifest['parts']]).select(F.col('value').alias('raw'))
    frame=(frame.withColumn('delivery_id',F.sha2('raw',256))
        .withColumn('ingested_at',F.current_timestamp())
        .withColumn('topic',F.lit(None).cast('string')).withColumn('partition',F.lit(None).cast('int'))
        .withColumn('offset',F.lit(None).cast('long')))
    root=f'lake/{dataset}/batch'
    consume_frame(frame,store,root)
    return root

def stream(spark,store,dataset,run,max_offsets):
    from pyspark.sql import functions as F
    state=store.json(f'runs/{run}/producer.json')
    if not state['complete'] or state['dataset']!=dataset:
        raise ValueError('Complete a matching finite producer run first')
    root=f'lake/{dataset}/stream/{run}'
    query=(spark.readStream.format('kafka')
        .option('kafka.bootstrap.servers',os.getenv('KAFKA_BOOTSTRAP_SERVERS','kafka:9092'))
        .option('subscribe',state['topic']).option('startingOffsets','earliest')
        .option('failOnDataLoss','true').option('maxOffsetsPerTrigger',max_offsets).load())
    query=(query.select(F.col('value').cast('string').alias('raw'),'topic','partition','offset')
        .withColumn('delivery_id',F.concat_ws(':','topic','partition','offset'))
        .withColumn('ingested_at',F.current_timestamp()))
    writer=(query.writeStream.option('checkpointLocation',store.uri(f'checkpoints/{run}'))
        .trigger(availableNow=True).foreachBatch(lambda frame,batch_id:consume_frame(frame,store,root)))
    writer.start().awaitTermination()
    # No later writes are permitted to the isolated, completed producer topic.
    bronze=spark.read.format('delta').load(store.uri(root+'/bronze'))
    actual={str(r['partition']):r['last']+1 for r in bronze.groupBy('partition').agg(F.max('offset').alias('last')).collect()}
    expected=state['end_offsets'][state['topic']]
    if actual!=expected: raise RuntimeError(f'Offset cutoff mismatch: {actual} != {expected}')
    store.json(f'runs/{run}/consumer.json',{'complete':True,'end_offsets':actual,'root':root})
    return root
