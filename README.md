# Data Forge

<img src="img/data-forge.svg" alt="Data Forge" class="light-mode-only">

The project is a **fully integrated ETL pipeline** designed to collect, transform, and analyze financial and economic data. It includes:  

- **Exchange rates** for multiple currencies across various financial institutions.  
- **Brazilian economic indexes**, with the potential to expand to MERCOSUR in the future.


## Features
- **Apache Airflow**: Workflow automation and orchestration.
- **PostgreSQL**: Database for Airflow metadata.
- **MinIO**: Object storage service.
- **Apache Spark**: Distributed data processing engine.
- **Kafka & Zookeeper**: Event streaming platform.
- **DBT (Data Build Tool)**: SQL-based transformation tool.
- **Metabase & Apache Superset**: Data visualization tools.
- **Docker Proxy**: Allows access to the Docker daemon over TCP.

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Kubernetes & kubectl

### Running the Services
To start all services:
```sh
make -f .makefile all-up
```
To stop all services:
```sh
make -f .makefile all-down
```
To start only Docker Compose services:
```sh
make -f .makefile compose-up
```
To stop Docker Compose services:
```sh
make -f .makefile compose-down
```
To deploy Kubernetes manifests:
```sh
make -f .makefile k8s-apply
```
To delete Kubernetes resources:
```sh
make -f .makefile k8s-delete
```

### Debug

```sh
docker exec -it <CONTAINER> sh
docker exec -it minio sh

```

```sh
docker logs <CONTAINER>
```

```sh
kubectl get pods -n default
```

```sh
kubectl describe pod <superset_pod_name>
kubectl logs <superset_pod_name>
```


## Services & Endpoints
| Service         | Description                   | URL                      | Working? |
|-----------------|-------------------------------|--------------------------|----------|
| PostgreSQL      | Airflow Metadata Database     | `localhost:5432`         | True     |
| DBT             | Data Build Tool               | `localhost:2376`         | True     |
| Airflow Web UI  | Workflow Management           | `http://localhost:8080`  | True     |
| MinIO Console   | S3 Storage Management         | `http://localhost:9001`  | True     |
| MinIO API       | S3-Compatible API             | `http://localhost:9000`  | True     |
| Spark Master UI | Spark Cluster Monitoring      | `http://localhost:8082`  | True     |
| Kafka           | Event Streaming Broker        | `http://localhost:9092`  | True     |
| Metabase        | BI and Data Exploration       | `http://localhost:30300` | True     |
| Apache Superset | Advanced Data Visualization   | `http://localhost:30088` | True     |
| Docker Proxy    | Docker Daemon Proxy           | `http://localhost:2376`  | True     |

## Contributors
- **Sara Fernandez** - Project Maintainer


