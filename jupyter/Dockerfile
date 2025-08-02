# ./jupyter/Dockerfile

FROM jupyter/pyspark-notebook

USER root

# Add custom libraries or settings here
RUN pip install psycopg2-binary

WORKDIR /home/jovyan/work