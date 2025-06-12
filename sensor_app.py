import time, os, json
import board, busio
from sensirion_i2c_scd4x import Scd4x
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
from prometheus_client import start_http_server, Gauge
import paho.mqtt.client as mqtt

# --- Metrics
gauges = {
    'co2': Gauge('room_co2_ppm', 'CO2 concentration in ppm'),
    'temperature': Gauge('room_temperature_c', 'Temperature in Celsius'),
    'humidity': Gauge('room_humidity_pct', 'Relative humidity percentage'),
    'co': Gauge('room_co_ppm', 'CO concentration in ppm'),
}

# --- MQTT config from env
def get_env(var, default=None):
    return os.getenv(var, default)

MQTT_BROKER   = get_env('MQTT_BROKER')
MQTT_PORT     = int(get_env('MQTT_PORT', 1883))
MQTT_USER     = get_env('MQTT_USER')
MQTT_PASSWORD = get_env('MQTT_PASSWORD')

# Start Prometheus HTTP server
start_http_server(8000)

# --- Setup I2C
i2c = busio.I2C(board.SCL, board.SDA)

# SCD41 CO2/T/H
scd = Scd4x(i2c)
scd.start_periodic_measurement()

# ADS1115 + CO sensor
ads = ADS1115(i2c, gain=1)
co_chan = AnalogIn(ads, ADS1115.P0)

# MQTT client
def on_connect(client, userdata, flags, rc):
    print(f"MQTT connected: {rc}")

mqttc = mqtt.Client()
mqttc.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqttc.on_connect = on_connect
mqttc.connect(MQTT_BROKER, MQTT_PORT)
mqttc.loop_start()

# Calibration stub
def voltage_to_co_ppm(v):
    baseline = 0.4  # clean-air reference
    scale = 200.0
    return max(0, (v - baseline) * scale)

try:
    while True:
        # Read sensors
        temp_raw, hum_raw, co2 = scd.read_measurement()
        temp = temp_raw / 100.0
        hum  = hum_raw  / 100.0
        vco  = co_chan.voltage
        co   = voltage_to_co_ppm(vco)

        # Update Prometheus gauges
        gauges['co2'].set(co2)
        gauges['temperature'].set(temp)
        gauges['humidity'].set(hum)
        gauges['co'].set(co)

        # Publish to MQTT for Home Assistant
        payload = json.dumps({
            'co2': co2,
            'temperature': temp,
            'humidity': hum,
            'co': co
        })
        mqttc.publish('home/air_quality/status', payload, qos=1)

        print(f"Metrics: CO₂={co2}, T={temp:.1f}, RH={hum:.1f}, CO={co:.1f}")
        time.sleep(5)

except KeyboardInterrupt:
    scd.stop_periodic_measurement()
    mqttc.loop_stop()
    print("Shutting down...")