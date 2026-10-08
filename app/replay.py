"""Finite replay: isolated topic per run, acknowledged checkpoints, explicit control."""
import json
import os
import time
from datetime import datetime, timezone
from app.acquire import events
from app.domain import digest,timestamp

def replay(store,dataset,run,speed=10,rate=100):
    from kafka import KafkaProducer,KafkaConsumer,TopicPartition
    from kafka.admin import KafkaAdminClient,NewTopic
    from kafka.errors import TopicAlreadyExistsError
    if speed<0 or rate<=0: raise ValueError('speed >= 0 and rate > 0 required')
    topic='df-'+digest(run.encode())[:24]
    ck=f'runs/{run}/producer.json'
    state=store.json(ck) if store.exists(ck) else {'dataset':dataset,'topic':topic,'next':0,'complete':False}
    if state['dataset']!=dataset: raise ValueError('Run bound to another dataset')
    if state['complete']: return state
    bootstrap=os.environ.get('KAFKA_BOOTSTRAP_SERVERS','kafka:9092')
    admin=KafkaAdminClient(bootstrap_servers=bootstrap)
    try: admin.create_topics([NewTopic(topic,1,1,topic_configs={'retention.ms':'86400000','retention.bytes':'5368709120'})])
    except TopicAlreadyExistsError: pass
    finally: admin.close()
    store.json(ck,state)
    producer=KafkaProducer(bootstrap_servers=bootstrap,acks='all',retries=5,
        max_in_flight_requests_per_connection=1,value_serializer=lambda e:json.dumps(e).encode())
    last_ts=None
    try:
        for seq,e in enumerate(events(store,dataset)):
            if seq<state['next']: continue
            control=f'runs/{run}/control.json'
            while store.exists(control) and store.json(control).get('paused',False): time.sleep(1)
            try: now_ts=timestamp(e['event_ts']).timestamp()
            except (ValueError,TypeError): now_ts=last_ts
            delay=1/rate
            if speed and now_ts is not None and last_ts is not None:
                delay=max(delay,max(0,now_ts-last_ts)/speed)
            time.sleep(delay)
            e.update(replay_run_id=run,replay_sequence=seq,producer_sent_at=datetime.now(timezone.utc).isoformat())
            producer.send(topic,key=e['instrument'].encode(),value=e).get(timeout=30)
            state['next']=seq+1
            if seq%100==0: store.json(ck,state)
            last_ts=now_ts
        producer.flush()
        consumer=KafkaConsumer(bootstrap_servers=bootstrap)
        try:
            tp=TopicPartition(topic,0)
            end=consumer.end_offsets([tp])[tp]
        finally: consumer.close()
        state.update(complete=True,end_offsets={topic:{'0':end}},completed_at=datetime.now(timezone.utc).isoformat())
        store.json(ck,state)
        return state
    finally:
        producer.close()
