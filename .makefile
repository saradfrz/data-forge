# Makefile

# Docker Compose file
COMPOSE_FILE := docker-compose.yaml

# Bring up Docker Compose services
.PHONY: compose-up
compose-up:
	sudo chmod 666 /var/run/docker.sock
	export DOCKER_HOST=unix:///var/run/docker.sock
	sudo chmod -R 777 ./etl
	docker network create ndsnet || true
	docker-compose -f $(COMPOSE_FILE) up -d

# Tear down Docker Compose services
.PHONY: compose-down
compose-down:
	docker-compose -f $(COMPOSE_FILE) down
	docker network rm ndsnet || true