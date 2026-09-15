FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY agent ./agent
COPY langgraph.json .

EXPOSE 2024

CMD [
  "langgraph",
  "dev",
  "--host",
  "0.0.0.0",
  "--port",
  "2024"
]