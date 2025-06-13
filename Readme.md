# Air-You-Dying-For?

<img src="./static/logo.png" width="200"/>

A tongue-in-cheek, Dockerized indoor air quality monitoring station that measures CO₂, CO, temperature, and humidity, exposes metrics for Prometheus/Grafana, and publishes states to Home Assistant via MQTT.

---

## 🔧 Hardware

* **Raspberry Pi 4B** (I²C bus, Docker host)
* **Sensirion SCD41**: High-accuracy CO₂, temperature, humidity (I²C)
* **DFRobot Fermion MEMS CO Sensor (SEN0564)**: 5–5000 ppm CO (analog)
* **ADS1115 16-bit ADC**: Converts CO sensor analog output to digital (I²C)
* Jumper wires, breadboard, 3.3 V power, optional enclosure

---

## 📁 Repository Structure

```
Air-You-Dying-For/
├── Dockerfile          # Builds sensor app image
├── docker-compose.yml  # Orchestrates Prometheus, Grafana, sensor_app
├── prometheus.yml      # Prometheus scrape config
├── sensor_app.py       # Reads sensors, exposes /metrics, MQTT client
└── README.md           # Project overview & instructions
```

---

## 🚀 Quickstart

1. **Clone** this repo to your Pi:

   ```bash
   git clone https://just5ky/Air-You-Dying-For.git
   cd Air-You-Dying-For
   ```

2. **Enable I²C** on the Pi:

   ```bash
   sudo raspi-config nonint do_i2c 0
   ```

3. **Launch** the stack:

   ```bash
   docker-compose up -d
   ```

4. **Verify** Prometheus metrics:

   * Browse to `http://<Pi_IP>:9090`
   * Check for metrics: `room_co2_ppm`, `room_co_ppm`, etc.

5. **Configure Grafana**:

   * Browse to your grafana instance.
   * Add Prometheus data source.
   * Import or build dashboards for CO₂, CO, temperature, humidity.

6. **Integrate with Home Assistant**:

   * Define an MQTT sensor in `configuration.yaml`:

     ```yaml
     sensor:
       - platform: mqtt
         name: "Room Air Quality"
         state_topic: "home/air_quality/status"
         value_template: "{{ value_json.co2 }}"
         json_attributes_topic: "home/air_quality/status"
     ```
   * Restart Home Assistant and observe the new sensor & attributes.

---

## 🛠️ File Descriptions

* **Dockerfile**: Installs Python dependencies (`sensirion-i2c-scd4x`, `adafruit-circuitpython-ads1x15`, `prometheus-client`, `paho-mqtt`), configures I²C tools, and runs `sensor_app.py`.

* **docker-compose.yml**:

  * **sensor_app**: Runs with `--privileged` for I²C, exposes `/metrics`, and publishes MQTT.

* **prometheus.yml**: Scrape targets for `air_quality` (your Python app) and Prometheus itself.

* **sensor_app.py**: Python script that:

  1. Reads CO₂, temperature, humidity from SCD41.
  2. Reads CO voltage from ADS1115 + MEMS sensor, applies calibration.
  3. Updates Prometheus Gauges.
  4. Publishes JSON to MQTT topic `home/air_quality/status`.
  5. Runs in an infinite loop with a 5 s interval.

---

## ⚙️ Configuration

All MQTT settings are configured via environment variables in `docker-compose.yml`:

```yaml
environment:
  - MQTT_BROKER=homeassistant.local
  - MQTT_PORT=1883
  - MQTT_USER=homeassistant
  - MQTT_PASSWORD=ha_pass
```

Prometheus scrape interval and targets are defined in `prometheus.yml`.

---

## 🧪 Calibration

1. Run the CO sensor in clean air to determine baseline voltage (`V₀`).
2. Expose the sensor to a known CO concentration (e.g., 100 ppm) and record voltage (`V₁`).
3. Compute slope: `scale = (100 ppm) / (V₁ - V₀)`.
4. Update the `voltage_to_co_ppm()` function in `sensor_app.py` with `baseline` and `scale` values.

---


*“Air-You-Dying-For?” – Because air is, like, so overrated.*
