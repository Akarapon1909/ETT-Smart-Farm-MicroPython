from ETSmartFarm import SHT31
import time

if __name__ == "__main__":
    sensor = SHT31()

    while True:
        temp = sensor.temperature()
        hum = sensor.humidity()

        print("Temperature: {:.2f} °C".format(temp))
        print("Humidity   : {:.2f} %".format(hum))
        print("------------------------")
        time.sleep(3)
