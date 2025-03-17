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
	docker-compose -f $(COMPOSE_FILE) up -d

# Tear down Docker Compose services
.PHONY: compose-down
compose-down:
	docker-compose -f $(COMPOSE_FILE) down

# Apply all Kubernetes manifests from the specified directory
.PHONY: k8s-apply
k8s-apply:
	kubectl apply -f $(K8S_DIR)

# Delete all Kubernetes resources defined in the manifests directory
.PHONY: k8s-delete
k8s-delete:
	kubectl delete -f $(K8S_DIR)

# Tear down all services (both Docker Compose and Kubernetes)
.PHONY: all-down
all-down: compose-down k8s-delete
