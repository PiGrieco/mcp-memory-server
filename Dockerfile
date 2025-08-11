FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/models \
    AUTO_TRIGGER_MODEL=PiGrieco/mcp-memory-auto-trigger-model

WORKDIR /app

# git aiuta i download HF; immagine ultra-minima
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# layer cache: deps prima del codice
COPY requirements.txt /app/requirements.txt

# HTTP deps espliciti (se non già nel requirements.txt)
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install fastapi uvicorn

# codice
COPY . /app

EXPOSE 8080

CMD ["uvicorn", "mcp_memory_server_http:app", "--host", "0.0.0.0", "--port", "8080"]
