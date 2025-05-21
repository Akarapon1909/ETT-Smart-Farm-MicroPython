from machine import I2C, Pin
from ETSmartFarm import SHT31
import time

if __name__ == "__main__":
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    sensor = SHT31(i2c)

    while True:
        try:
            temp = sensor.temperature()
            hum = sensor.humidity()
            print("Temperature: {:.2f} °C".format(temp))
            print("Humidity: {:.2f} %".format(hum))
        except Exception as e:
            print("Error reading SHT31 sensor:", e)
        time.sleep(2)
