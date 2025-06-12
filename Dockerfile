# Use official slim Python runtime
FROM python:3.11-slim

# Install OS dependencies for I2C
RUN apt-get update && \
    apt-get install -y --no-install-recommends i2c-tools && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy application
COPY sensor_app.py .

# Install Python dependencies
RUN pip install --no-cache-dir \
    sensirion-i2c-scd4x \
    adafruit-circuitpython-ads1x15 \
    prometheus-client \
    paho-mqtt

# Expose metrics port
EXPOSE 8000

# Entrypoint
CMD ["python", "sensor_app.py"]