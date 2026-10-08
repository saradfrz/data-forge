.PHONY: up test web airflow trigger status
up:
	bash scripts/bootstrap.sh
test:
	python -m pytest tests -q
web:
	kubectl --context kind-data-forge -n data-forge port-forward svc/web 8088:8080
airflow:
	kubectl --context kind-data-forge -n data-forge port-forward svc/airflow 8080:8080
trigger:
	kubectl --context kind-data-forge -n data-forge exec deployment/airflow -- airflow dags trigger data_forge
status:
	kubectl --context kind-data-forge -n data-forge get pods,pvc
