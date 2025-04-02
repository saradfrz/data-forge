# Makefile

# Docker Compose file
COMPOSE_FILE=docker-compose.yaml

# Kubernetes manifests directory (adjust if you use individual files)
K8S_DIR=k8s

# Default target: bring everything up
.PHONY: all-up
all-up: compose-up k8s-apply

# Bring up Docker Compose services
.PHONY: compose-up
compose-up:
	docker network create ndsnet
	docker-compose -f $(COMPOSE_FILE) up -d
	sudo chmod 666 /var/run/docker.sock
	export DOCKER_HOST=unix:///var/run/docker.sock

# Tear down Docker Compose services
.PHONY: compose-down
compose-down:
	docker-compose -f $(COMPOSE_FILE) down

# Apply all Kubernetes manifests from the specified directory
.PHONY: k8s-apply
k8s-apply:
	docker network create ndsnet
	kubectl apply -f $(K8S_DIR)

# Delete all Kubernetes resources defined in the manifests directory
.PHONY: k8s-delete
k8s-delete:
	kubectl delete -f $(K8S_DIR)
	docker network rm ndsnet

# Tear down all services (both Docker Compose and Kubernetes)
.PHONY: all-down
all-down: 
	compose-down 
	k8s-delete
	docker network rm ndsnet


# Bring up only specific Docker Compose services

# spark pipeline
.PHONY: compose-up-spark
compose-up-spark:
	docker network create ndsnet
	docker-compose -f $(COMPOSE_FILE) up -d jupyter spark-worker spark-master minio-setup minio minio-webhook

.PHONY: compose-down-spark
compose-down-spark:
	docker-compose -f $(COMPOSE_FILE) down jupyter spark-worker spark-master minio-setup minio minio-webhook
	docker network rm ndsnet


# spark pipeline
.PHONY: compose-up-robots
compose-up-robots:
	docker network create ndsnet
	docker-compose -f $(COMPOSE_FILE) up -d robots postgres minio-setup minio minio-webhook airflow-init airflow-webserver airflow-scheduler
	kubectl apply -f $(K8S_DIR)/dbt-deployment.yaml
	kubectl apply -f $(K8S_DIR)/dbt-service.yaml
	sudo chmod 666 /var/run/docker.sock
	export DOCKER_HOST=unix:///var/run/docker.sock

.PHONY: compose-down-robots
compose-down-robots:
	docker-compose -f $(COMPOSE_FILE) down robots postgres minio-setup minio minio-webhook airflow-init airflow-webserver airflow-scheduler
	kubectl delete -f $(K8S_DIR)/dbt-deployment.yaml
	kubectl delete -f $(K8S_DIR)/dbt-service.yaml
	docker network rm ndsnet

