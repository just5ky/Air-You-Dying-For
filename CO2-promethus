import os
import time
import board
import adafruit_scd4x
from prometheus_client import start_http_server, Gauge
import logging

logging.basicConfig(level=logging.INFO)

# Read environment variables
PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', 8000))

# Set up Prometheus metrics
co2_gauge = Gauge('co2_ppm', 'CO2 level in PPM')
temperature_gauge = Gauge('temperature_celsius', 'Temperature in Celsius')
humidity_gauge = Gauge('humidity_percent', 'Relative humidity in percent')

# Start Prometheus HTTP server
start_http_server(PROMETHEUS_PORT)
logging.info(f"Prometheus exporter started on port {PROMETHEUS_PORT}")

# Initialize SCD41 sensor
try:
    i2c = board.I2C()
    scd4x = adafruit_scd4x.SCD4X(i2c)
    scd4x.start_periodic_measurement()
    logging.info("SCD41 sensor initialized")
except (ValueError, RuntimeError) as e:
    logging.error(f"Error initializing sensor: {e}")
    exit(1)

# Main loop
while True:
    try:
        if scd4x.data_ready:
            co2_ppm = scd4x.CO2
            temperature_c = scd4x.temperature
            humidity = scd4x.relative_humidity

            # Update Prometheus gauges
            co2_gauge.set(co2_ppm)
            temperature_gauge.set(temperature_c)
            humidity_gauge.set(humidity)

            logging.info(f"CO2: {co2_ppm} PPM, Temp: {temperature_c} °C, Humidity: {humidity} %")
        time.sleep(2)
    except KeyboardInterrupt:
        logging.info("Stopping script")
        break
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        break
