from ETSmartFarm import Wifi

def mqtt_callback(topic, msg):
    print("Received:", topic, msg)

def publish_example():
    print("Publishing to MQTT...")
    wifi_mqtt.publish("smartfarm/status", "Online")

def main():
    wifi_mqtt = Wifi(
        ssid="YourSSID",
        password="YourPassword",
        mqtt_broker="broker.hivemq.com",
        mqtt_port=1883,
        mqtt_client="esp32_client_001",
        mqtt_user="",
        mqtt_pass="",
        topic_sub=b"smartfarm/command",
        callback=mqtt_callback
    )

    wifi_mqtt.connect_wifi()
    wifi_mqtt.connect_mqtt()
    wifi_mqtt.auto_loop(publish_callback=publish_example, interval_ms=10000)

if __name__ == "__main__":
    main()