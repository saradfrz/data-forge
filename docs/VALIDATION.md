# Validation record

As of 8 October 2026. This is a generated MVP with tested financial primitives and supplied deployment code, not a certified cluster deployment.

| Check | Result | Boundary |
|---|---|---|
| Python compilation | Passed | Application, API, models, scripts and DAG syntax |
| Full Python suite with `DF_TEST_SPARK=1` | 7 passed in 162.86 seconds | Includes actual local Spark 3.5.6 candle/return/volatility computations; does not include Delta or Kafka connectors |
| Final fast regression suite | 6 passed, 1 opt-in Spark test skipped | Rechecked immutable ingestion including changed mapping and synthetic status, numerical rules, API and comparison logic |
| Framework preservation | Passed | ASTs of all five supplied utility modules match the template; `main.py` retains its cleanup, logging and exception structure with the application import/call inserted |
| Frontend dependency install and production build | Passed | `npm ci`, `npm run build`; not browser interaction testing |
| Static synthetic snapshot | Generated | 230 original rows, 228 accepted, 2 quarantined; reference result explicitly says reconciliation `not_run` |
| Kubernetes YAML parsing | Passed, 20 resource documents | Parsing is not Kubernetes server validation |
| Filesystem-mode CLI ingestion | Passed | Does not establish S3/MinIO connectivity |
| Delta-backed batch attempt | Blocked | Maven host resolution for Delta, Spark Kafka and Hadoop AWS artifacts failed in this environment; no Delta success claimed |
| Container builds and Kubernetes deployment | Not run | Docker, kind, kubectl and Helm are unavailable in this execution environment |
| Airflow DAG, actual Kafka replay and S3 recovery | Not run | Require local deployment and the acceptance checks below |

The test environment used host Python 3.12; application images pin Python 3.11. The test suite emitted one upstream Starlette/AnyIO deprecation warning. The Spark metric test was executed before final ingestion and chart corrections; those corrections do not change Spark financial transformations.

## Reproduce the checks

From the repository root after installing `requirements-dev.txt`:

```bash
python -m pytest tests -q
DF_TEST_SPARK=1 SPARK_LOCAL_IP=127.0.0.1 python -m pytest tests -q
python -m compileall -q app api models main.py airflow/dags scripts
cd web
npm ci
npm run build
```

## Deployment acceptance gates

1. Run `make up`; verify all six deployments become ready, image builds finish and Spark resolves its connectors. Record image IDs and dependency versions. Image/dependency compatibility remains a deployment risk until this succeeds.
2. Trigger the synthetic DAG. Require a passing reconciliation, 228 accepted and 2 quarantined source events in both paths, and an API snapshot with a real run ID. The bundled reference preview is not evidence of this result.
3. Rerun each stage against the same dataset/run and compare row counts and Gold values. Attempt a changed CSV or mapping with the same dataset ID and require rejection.
4. Interrupt replay and restart it; require identical source-event sets after deduplication. Restart the consumer with retained checkpoint. Test an expired topic separately and require explicit failure and a new replay run.
5. Pause/resume replay; introduce out-of-order timestamps and equal-timestamp distinct rows. Require deterministic final candles at the completed offset cutoff.
6. Stop MinIO during a task and restore it. Require task failure/retry, retained raw objects and checkpoints, and preservation of the previous published pointer. Restart pods and verify PVC data survives.
7. Mutate a Gold metric in an isolated test dataset; reconciliation must fail and publication must be refused. Reconcile again after every Gold rebuild; do not publish using an old pass after manual table edits. This MVP assumes serialized writers and does not bind a report to Delta version IDs.
8. Review charts with a missing-minute interval, switch between reference and cluster modes, stop the API, and verify the error message and last successful snapshot remain unambiguous. Check timestamp spacing, labels, truncation warnings and partial-day labels.
9. Measure actual resource usage and source volume before expanding beyond the synthetic fixture. A 2-million-record trading day is a sizing target, not a benchmark result.

Keep cluster logs, reconciliation JSON, source manifest and screenshots as portfolio evidence. Do not describe these gates as passed until they have been executed.
