# 📊 Data Forge

<p align="center">
  <img src="img/DataForge.png" alt="Data Forge" width="300">
  <br>
</p>

**Fully Dockerized Data Engineering Portfolio Project**  
*Following the Medallion Architecture (Bronze → Silver → Gold)*

This project simulates a real-world ETL pipeline using Spark, PostgreSQL, and Jupyter — all orchestrated with Docker Compose.

---

## 🧱 Architecture Overview

- **Bronze Layer**: Raw JSON stored locally
- **Silver Layer**: Cleaned & normalized data in PostgreSQL (dev/prod schemas)
- **Gold Layer**: BI-ready Parquet datasets for analytics
- **Tools**: Spark, Jupyter, PostgreSQL

---

## 🌐 Service Access (Localhost URLs)

| Service          | URL                             | Description                     |
|------------------|----------------------------------|---------------------------------|
| **Jupyter Lab**  | [localhost:8888](http://localhost:8888) | Notebook-based dev environment |
| **Spark Master** | [localhost:8082](http://localhost:8082) | Spark Web UI                   |
| **Spark Worker** | [localhost:8081](http://localhost:8081) | Worker node monitoring         |
| **Docker API**   | [localhost:2376](http://localhost:2376) | Proxy access to Docker socket  |

---

## 🛠️ Project Initialization

### ▶️ Start All Services

```bash
 make -f .makefile compose-up
```

This will:

* Create a shared Docker network (`ndsnet`)
* Launch all containers in detached mode
* Fix permissions on Docker socket

Note: If you get the error 
```bash
Error response from daemon: network with name ndsnet already exists
```

run
```bash
docker network rm ndsnet
```

### ⛔ Stop All Services

```bash
 make -f .makefile compose-down
```

This will:

* Stop and remove containers
* Remove the `ndsnet` network

---

## 📁 Folder Structure (Essential)

```bash
.
├── etl/
│   ├── bronze/           # Raw input JSONs
│   └── gold/             # Final Parquet tables
├── jupyter/              # Jupyter Dockerfile + notebooks
├── robots/               # Optional custom service
├── spark/src/            # Spark ETL jobs
├── Makefile
└── docker-compose.yaml
```

## Installing the project for the first time
- Install Docker
- Install WSL distro: ``
- Configure git 
- Clone project

With Docker open: 
- Run `sudo apt install make`
- Rename `jupyter/notebooks/env_example` to `jupyter/notebooks/.env` and `env_example` to `.env`
- Execute
```bash
wget -O /tmp/postgresql-42.7.3.jar \
https://jdbc.postgresql.org/download/postgresql-42.7.3.jar && \
sudo mv /tmp/postgresql-42.7.3.jar ./spark/jars/
```
- Run `make -f .makefile compose-up`

---

## 📄 Project Maintainer
Sara Fernandez 