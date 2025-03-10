# Data Forge

<img src="img/data-forge.svg" alt="Data Forge" class="light-mode-only">

This project sets up a complete data pipeline and analytics platform using Docker Compose and Kubernetes. The platform includes data ingestion, transformation, storage, and visualization tools.

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
- Helm (optional for advanced Kubernetes deployment)

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
kubectl get pods -n default
```

```sh
kubectl describe pod <superset_pod_name>
kubectl logs <superset_pod_name>
```

```sh
kubectl describe pod dbt-6cb67fffb4-ppszz
kubectl logs superset-54759c54fb-kfhdh 

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
| Kafka           | Event Streaming Broker        | `http://localhost:9092`  | False    |
| Metabase        | BI and Data Exploration       | `http://localhost:30300` | True     |
| Apache Superset | Advanced Data Visualization   | `http://localhost:30088` | True     |
| Docker Proxy    | Docker Daemon Proxy           | `http://localhost:2376`  | True     |


## Architecture Overview
The system is deployed in a hybrid model using both Docker Compose and Kubernetes.
- Docker Compose handles local development services.
- Kubernetes is used for scalable production deployments.

## Data Pipeline Flow
1. **Data Ingestion**: Kafka collects and streams events.
2. **Storage**: Events are stored in MinIO and PostgreSQL.
3. **Transformation**: DBT runs SQL-based transformations.
4. **Orchestration**: Airflow schedules jobs.
5. **Analytics & Visualization**: Metabase and Superset provide insights.

## Future Enhancements
- Implement CI/CD pipeline.
- Add monitoring with Prometheus & Grafana.
- Expand with additional machine learning pipelines.


## Contributors
- **Sara Fernandez** - Project Maintainer

## License
This project is licensed under the MIT License.

