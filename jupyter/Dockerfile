

FROM jupyter/pyspark-notebook

USER root

RUN pip install --upgrade pip && \
    pip install psycopg2-binary python-dotenv 

RUN mkdir -p /home/jovyan/.jupyter && \
    echo "c.ServerApp.token = ''" >> /home/jovyan/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.password = ''" >> /home/jovyan/.jupyter/jupyter_server_config.py && \
    chown -R jovyan:users /home/jovyan/.jupyter


RUN mkdir -p /home/jovyan/.local/share/jupyter/runtime && \
    chown -R jovyan:users /home/jovyan/.local

USER jovyan

RUN python -m ipykernel install --user --name=spark-postgres --display-name "PySpark + Postgres"

USER root
