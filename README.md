# 📊 Data Forge

<p align="center">
  <img src="img/DataForge.png" alt="Data Forge" width="300">
  <br>
  <img src="img/DataForge500.png" alt="Data Forge 500" width="150">
</p>


**Fully Dockerized Data Engineering Portfolio Project**  
*Following the Medallion Architecture (Bronze → Silver → Gold)*

This project simulates a real-world ETL pipeline using Spark, PostgreSQL, Trino, Airflow, and Jupyter — all orchestrated with Docker Compose.

---

## 🧱 Architecture Overview

- **Bronze Layer**: Raw JSON stored locally
- **Silver Layer**: Cleaned & normalized data in PostgreSQL (dev/prod schemas)
- **Gold Layer**: BI-ready Parquet datasets queried via Trino
- **Tools**: Spark, Jupyter, Trino, Airflow, PostgreSQL

---

## 🌐 Service Access (Localhost URLs)

| Service          | URL                             | Description                     |
|------------------|----------------------------------|---------------------------------|
| **Airflow**      | [localhost:8080](http://localhost:8080) | Workflow orchestration         |
| **Trino**        | [localhost:8088](http://localhost:8088) | SQL query engine for Parquet   |
| **Jupyter Lab**  | [localhost:8888](http://localhost:8888) | Notebook-based dev environment |
| **Spark Master** | [localhost:8082](http://localhost:8082) | Spark Web UI                   |
| **Spark Worker** | [localhost:8081](http://localhost:8081) | Worker node monitoring         |
| **Docker API**   | [localhost:2376](http://localhost:2376) | Proxy access to Docker socket  |

---

## 🛠️ Project Initialization

### ▶️ Start All Services

```bash
make compose-up
````

This will:

* Create a shared Docker network (`ndsnet`)
* Launch all containers in detached mode
* Fix permissions on Docker socket and Trino configs

### ⛔ Stop All Services

```bash
make compose-down
```

This will:

* Stop and remove containers
* Remove the `ndsnet` network

---

## 🧯 Troubleshooting

### 🐳 Docker Socket Permission Error

```bash
sudo chmod 666 /var/run/docker.sock
```

Or re-run `make compose-up` to reset permissions.

---

### 🐘 Can't Connect to Postgres?

Verify:

* `silver-postgres` is running:

  ```bash
  docker ps | grep silver-postgres
  ```
* Network connection:

  ```bash
  docker exec -it jupyter ping silver-postgres
  ```

---

### 🧪 Trino Doesn’t Show Tables?

Ensure:

* Your Parquet files are saved in `/data/gold`
* Trino `hive.properties` points to `/data/gold`
* Use this in Trino CLI:

  ```sql
  SHOW TABLES FROM hive.default;
  ```

---

### 🔁 Rebuild Specific Services

```bash
docker-compose build jupyter
docker-compose up -d jupyter
```

---

## 📁 Folder Structure (Essential)

```bash
.
├── airflow/              # DAGs, logs, plugins
├── etl/
│   ├── bronze/           # Raw input JSONs
│   └── gold/             # Final Parquet tables
├── jupyter/              # Jupyter Dockerfile + notebooks
├── robots/               # Optional custom service
├── spark/src/            # Spark ETL jobs
├── trino/etc/            # Config files + catalog definitions
├── Makefile
└── docker-compose.yaml
```

---

## 📄 Project Mantinar
Sara Fernandes - saradfrz@gmail.com
