# Data Forge

<img src="img/data-forge.svg" alt="Data Forge" class="light-mode-only">

This project serves as a comprehensive base repository for building ETL pipelines, testing cutting-edge data technologies, and simulating cloud services locally—without incurring cloud costs.

The architecture integrates Apache Airflow, Apache Spark, AWS Glue, MinIO, PostgreSQL, and Jupyter to facilitate end-to-end data processing, orchestration, and analytics. It also includes AWS Lambda emulation for serverless computing, as well as a MinIO webhook for event-driven workflows.

By leveraging Docker and Kubernetes, this framework enables seamless experimentation with distributed computing, cloud storage, and real-time data processing, making it a valuable resource for data engineers and software developers exploring new technologies in a local environment.

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

### Running custom pipelines

```sh
make -f .makefile compose-up-spark
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
| Service           | Ports                                        | Platform    |
|-------------------|----------------------------------------------|-------------|
| Airflow Init      | N/A                                          | Docker      |
| Airflow Scheduler | 8080/tcp                                     | Docker      |
| Airflow Webserver | 0.0.0.0:8080->8080/tcp                         | Docker      |
| AWS Glue          | localhost:30300                              | Docker      |
| AWS Lambda        | 0.0.0.0:9010->8080/tcp                         | Docker      |
| DBT               | localhost:2376                               | Kubernetes  |
| Docker Proxy      | 0.0.0.0:2376->2375/tcp                         | Docker      |
| Hive Metastore    | localhost:9083                               | Kubernetes  |
| Hive Server       | localhost:10000                              | Kubernetes  |
| Jupyter           | 0.0.0.0:8888->8888/tcp                         | Docker      |
| Kafka             | localhost:9092                               | Kubernetes  |
| Metabase          | http://localhost:30300                         | Kubernetes  |
| MinIO             | 0.0.0.0:9000-9001->9000-9001/tcp                 | Docker      |
| MinIO Setup       | N/A                                          | Docker      |
| MinIO Webhook     | 0.0.0.0:5000->5000/tcp                         | Docker      |
| PostgreSQL        | 0.0.0.0:5432->5432/tcp                         | Docker      |
| Spark Master      | 0.0.0.0:7077->7077/tcp, 0.0.0.0:8082->8080/tcp    | Docker      |
| Spark Worker      | 0.0.0.0:8081->8081/tcp                         | Docker      |
| Superset          | http://localhost:30088                         | Kubernetes  |
| Zookeeper         | 2181                                         | Kubernetes  |



## Contributors
- **Sara Fernandez** - Project Maintainer


