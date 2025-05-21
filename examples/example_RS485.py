from ETSmartFarm import RS485
import time

if __name__ == "__main__":
    rs485 = RS485()

    while True:
        data = rs485.read_all()
        print("Sensor Data:", data)
        time.sleep(5)
