# Data Forge

A local Kubernetes financial data engineering lab by Sara Fernandez: **Airflow → Kafka → Spark/Delta → MinIO → FastAPI/React**.

This version evolves your existing Spark/medallion Data Forge project into an FX quote replay platform. Databricks and dbt are reserved for a separate single-CSV project. No paid cloud account is required. This archive contains code, fixtures, deployment manifests, planning reports and tests; see `docs/VALIDATION.md` for exactly what was executed.

## What works in the implementation

- Import a canonical CSV into an immutable raw archive and chunked transport envelopes.
- Validate quotes, preserve timestamp ties, and quarantine invalid records.
- Build batch and independently ingested Kafka paths into Delta Bronze/Silver.
- Replay with rate/speed controls, acknowledged producer checkpoints and pause/resume control objects.
- Consume a completed replay with Spark Structured Streaming `AvailableNow` and durable checkpoints.
- Compute bid/ask/midpoint OHLC (1s, 1m, 1h), observation-weighted spreads, minute returns, rolling volatility and UTC daily summaries in Spark.
- Compare event sets and financial tables; publish only after a passing reconciliation.
- Run bounded stages as Kubernetes pods launched by Airflow. Persist data/checkpoints in MinIO.
- Explore the React dashboard in bundled synthetic mode or against the cluster's published snapshot.

This is a **bounded replay MVP**. It does not yet implement a continuously running watermark/window service, certified market calendars, automatic source downloads, multi-node Spark, high availability, a live broker-lag dashboard or 2M/day benchmarks. Daily completeness stays false until acquisition-calendar verification is implemented. Do not mistake manifests supplied here for an already-tested Kubernetes deployment.

## Prerequisites

Use Linux or WSL2 on Windows, with Docker, kind, kubectl, Python 3 and make. Budget about 10–12 GB for the cluster plus the host OS; a 20 GB laptop should run one task at a time, subject to measurement. Allow 40 GB spare disk for images, PVCs and temporary files. Only one kind node and one Spark task are used initially; Spark runs `local[2]` **inside a Kubernetes pod**, not a distributed Spark executor cluster.

Image builds need internet access to package repositories. MinIO Community is built from the pinned source release because its repository is archived and source-only. This is an isolated personal lab, not a production storage recommendation. See `docs/DEPENDENCIES.md`.

## Launch the Kubernetes stack

```bash
make up
make status
```

Bootstrap generates a private `.env` once, creates a dedicated kind cluster, builds/loads local images, applies manifests and waits for services. It does not mount the Docker socket into a pod or change socket permissions. Existing `.env` files are reused; if you created one from `.env.example`, fill all values before bootstrapping.

Run these in separate terminals:

```bash
make airflow
make web
```

Open Airflow at http://localhost:8080 and Data Forge at http://localhost:8088. Airflow's standalone development mode uses SimpleAuthManager. Retrieve the generated admin password locally with:

```bash
kubectl --context kind-data-forge -n data-forge exec deployment/airflow -- cat /opt/airflow/logs/simple_auth_passwords.json
```

Keep that output private. The web dashboard starts in **bundled synthetic demo** mode. Select **Local cluster snapshot** after completing a DAG run.

```bash
make trigger
```

The DAG executes: ingest fixture → batch → batch Gold → finite replay → stream → stream Gold → reconcile → publish. DAG retries reuse the same run ID. There is only one active run and one writer to each Delta path. Airflow uses PostgreSQL metadata and LocalExecutor; KubernetesPodOperator launches the data tasks. PostgreSQL is not a market-data warehouse here.

## Dataset contract and real CSV imports

The included fixture is synthetic and freely editable. Required canonical CSV columns are `instrument,event_ts,bid,ask`; volume columns are optional. Use ISO timestamps with an explicit timezone and decimal-point prices. Inspect any Dukascopy export before importing it. `contracts/csv-mapping.example.json` is a mapping example, **not a verified description of your export**. Its timestamp format includes `%z`, so the source must actually contain an offset. Configure to match inspected data; never silently treat local timestamps as UTC.

A dataset contains one canonical CSV in v0.1; combine/sort source files offline only with a documented manifest and without removing timestamp ties. Renaming or modifying source bytes requires a new dataset ID. Import is idempotent for the same bytes. Raw file SHA + original row index defines event identity.

For a real CSV, start the configured temporary app pod and copy the file into its disposable filesystem:

```bash
kubectl --context kind-data-forge apply -f infra/k8s/manual-task.yaml
kubectl --context kind-data-forge -n data-forge wait --for=condition=Ready pod/forge-task --timeout=120s
kubectl --context kind-data-forge -n data-forge cp input/quotes.csv forge-task:/tmp/quotes.csv
kubectl --context kind-data-forge -n data-forge exec forge-task -- python main.py ingest --csv /tmp/quotes.csv --dataset eurusd-sample
```

Run subsequent commands in that pod, or adapt the DAG's dataset and input parameters after a verified import. The shipped DAG intentionally targets the synthetic fixture and never overwrites a real dataset.

## CLI stage sequence

Inside an app pod with S3 and Kafka environment configured:

```bash
python main.py ingest --synthetic --dataset fixture-v1
python main.py batch --dataset fixture-v1
python main.py gold --dataset fixture-v1 --path batch
python main.py replay --dataset fixture-v1 --run demo-v1 --speed 0 --rate 100
python main.py stream --dataset fixture-v1 --run demo-v1
python main.py gold --dataset fixture-v1 --run demo-v1 --path stream
python main.py reconcile --dataset fixture-v1 --run demo-v1
python main.py publish --dataset fixture-v1 --run demo-v1
```

Use a new `--run` for a new experiment. A completed producer run is a no-op on retry. `--speed 0` removes event-time sleeps while retaining `--rate`; positive speed scales original time gaps. Pause/resume from a **different pod** using `python main.py pause --run demo-v1` and `resume`. Do not run concurrent CLI commands in the same working directory: the mandated template resets its local scratch/log folders at startup. Durable source and lake paths are never those folders.

The first Spark command downloads matching Maven connectors. If dependency retrieval is blocked, resolve approved artifacts into the image before running tasks; do not change versions arbitrarily. Kafka retention is one day with a size cap; resume beyond retention must fail, followed by a new run rebuilt from raw.

## Testing and offline preview

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest tests -q
DF_TEST_SPARK=1 python -m pytest tests/test_spark_metrics.py -q
PYTHONPATH=. python scripts/build_static_fixture.py
cd web
npm ci
npm run dev
```

The static generator is a small-fixture reference implementation. It labels reconciliation **not_run** and makes no Kafka/Delta claim. Cluster publication is a separate result. API responses contain bounded JSON previews; complete Gold Parquet exports stay in MinIO. No browser credentials are required.

## Persistence and recovery

MinIO, Kafka, PostgreSQL and Airflow logs have PVCs. Deleting/restarting a pod preserves them; deleting the kind cluster destroys the lab's disks. Export wanted objects before removing a cluster. No teardown target deletes data implicitly. The raw archive and producer/consumer checkpoints allow replay recovery; topic retention is not an archive.

Inspect logs with `kubectl --context kind-data-forge -n data-forge logs deployment/airflow` and the Airflow task log viewer. Failed stages leave the last good published pointer intact. Reconciliation reports identify missing/extra keys and mismatches. Backpressure, restarts against real Kafka, S3 outage and PVC recovery are deployment acceptance tests in the PM report, not claimed completed here.

## Framework compatibility and migration

The mandated `load_config`, logger, file, directory and string utilities are preserved. `main.py` only fills the missing import and application call. The inherited logger name remains `invoice_pipeline`; the wrapper logs command names and stdout is captured by Airflow. `config.dir.output_html` is mapped to disposable `output/session`, never MinIO/checkpoints/input. See `docs/MIGRATION.md` for the starter-to-new-code mapping.

Reports retain the requested download filenames `TickStream_Lakehouse_PM_Report.md` and `TickStream_Lakehouse_Finance_Theory.md`, but their title and active architecture are Data Forge.
