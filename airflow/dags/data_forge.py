"""Bounded run; pipeline state in MinIO survives task pod replacement."""
from datetime import datetime,timezone,timedelta
from airflow.sdk import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s

with DAG('data_forge',start_date=datetime(2026,1,1,tzinfo=timezone.utc),schedule=None,
         catchup=False,max_active_runs=1,default_args={'retries':1,'retry_delay':timedelta(seconds=30)},
         tags=['portfolio','fx','kubernetes']) as dag:
    run="{{ dag_run.run_id | replace(':','') | replace('+','') | replace('.','') }}"
    def task(name,args):
        return KubernetesPodOperator(task_id=name,name='forge-'+name,namespace='data-forge',
            image='data-forge/app:0.1.0',image_pull_policy='IfNotPresent',
            cmds=['python','main.py'],arguments=args+['--dataset','fixture-v1','--run',run],
            in_cluster=True,get_logs=True,on_finish_action='delete_pod',
            startup_timeout_seconds=600,execution_timeout=timedelta(minutes=40),
            env_from=[k8s.V1EnvFromSource(secret_ref=k8s.V1SecretEnvSource(name='forge-secrets'))],
            env_vars={'S3_ENDPOINT':'http://minio:9000','KAFKA_BOOTSTRAP_SERVERS':'kafka:9092'},
            container_resources=k8s.V1ResourceRequirements(requests={'cpu':'500m','memory':'1Gi'},limits={'cpu':'2','memory':'5Gi'}))
    a=task('ingest',['ingest','--synthetic'])
    b=task('batch',['batch'])
    c=task('gold_batch',['gold','--path','batch'])
    d=task('replay',['replay','--speed','0','--rate','100'])
    e=task('stream',['stream'])
    f=task('gold_stream',['gold','--path','stream'])
    g=task('reconcile',['reconcile'])
    h=task('publish',['publish'])
    a >> b >> c >> d >> e >> f >> g >> h
