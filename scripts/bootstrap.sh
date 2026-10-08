#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for bin in docker kind kubectl python3; do command -v "$bin" >/dev/null || { echo "Missing: $bin"; exit 1; }; done
python3 scripts/secrets.py
if ! kind get clusters | grep -qx data-forge; then
  kind create cluster --name data-forge --config infra/kind.yaml
fi
for component in app minio airflow web; do
  docker build -t "data-forge/$component:0.1.0" -f "docker/$component.Dockerfile" .
  kind load docker-image "data-forge/$component:0.1.0" --name data-forge
done
kubectl --context kind-data-forge apply -f infra/k8s/stack.yaml
kubectl --context kind-data-forge -n data-forge create secret generic forge-secrets --from-env-file=.env --dry-run=client -o yaml | kubectl --context kind-data-forge apply -f -
for service in minio postgres kafka airflow api web; do
  kubectl --context kind-data-forge -n data-forge rollout status "deployment/$service" --timeout=600s
done
echo 'Ready. Run make airflow and make web in separate terminals.'
