# Lighting_System_for_Smart_Agriculture
SmartFarmBot is an intelligent IoT-based system that combines environmental sensing, automated lighting control, real-time image capture, and cloud integration to monitor crop conditions in a smart agriculture environment.

## Feature
### Edge Sensor Integration (ESP32)
    Reads soil temperature, humidity, pH, nitrogen (N), phosphorus (P), and potassium (K) values via RS485 sensor
    Sends data over Serial to a Raspberry Pi system

### Serial Communication
    Parses sensor values with automatic data extraction and MQTT publishing

### LED Light Control
    Controls RGB+White+UV grow lights with PWM via serial command to microcontroller

### Raspberry Pi Image System
    Captures annotated images with environmental overlays (weather, sensor data)
    Automatically uploads captured images to Google Photos

### Data Overlay
    Shows weather forecasts from external APIs (via MQTT) and real-time edge sensor data
    Custom overlay on images using OpenCV

### Google Photos Backup
    Uploads every captured image to your cloud photo storage

### MQTT Communication
    Publishes edge sensor values to specific MQTT topics
    Subscribes to weather and air quality data