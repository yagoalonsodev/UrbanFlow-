FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY agent ./agent
COPY langgraph.json .

ENV PYTHONPATH="/app"

CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "2024"]