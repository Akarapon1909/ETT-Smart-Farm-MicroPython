from machine import I2C, Pin
from ETSmartFarm import BH1750
import time

if __name__ == "__main__":
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))
    sensor = BH1750(i2c)

    while True:
        lux = sensor.read_lux()
        if lux is not None:
            print("Light Intensity: {:.2f} lux".format(lux))
        else:
            print("Failed to read light intensity.")
        time.sleep(2)
