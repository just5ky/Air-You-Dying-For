FROM python:3.14.7-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.14.7-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    i2c-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY scd41_monitor.py .

ENV PROMETHEUS_PORT=8000

EXPOSE ${PROMETHEUS_PORT}

CMD ["python", "-u", "scd41_monitor.py"]
