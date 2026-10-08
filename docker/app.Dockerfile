FROM python:3.11.11-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-17-jre-headless curl tini && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/data-forge
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -u 10001 -m forge && mkdir -p /home/forge/.ivy2 && chown -R forge /opt/data-forge /home/forge
COPY --chown=forge:forge . .
ENV PYTHONPATH=/opt/data-forge PYSPARK_PYTHON=python SPARK_LOCAL_IP=127.0.0.1
USER forge
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "main.py", "--help"]
