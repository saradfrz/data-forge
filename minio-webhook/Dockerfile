FROM python:3.9

WORKDIR /app
COPY webhook.py /app/
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["python", "/app/webhook.py"]
