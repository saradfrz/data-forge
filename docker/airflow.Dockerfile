FROM apache/airflow:3.3.2-python3.11
RUN pip install --no-cache-dir "apache-airflow==3.3.2" apache-airflow-providers-cncf-kubernetes \
    --constraint https://raw.githubusercontent.com/apache/airflow/constraints-3.3.2/constraints-3.11.txt
COPY --chown=airflow:root airflow/dags /opt/airflow/dags
