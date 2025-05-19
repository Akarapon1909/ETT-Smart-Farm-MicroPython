from ETSmartFarm import Display
import time

if __name__ == "__main__":
    display = Display()

    display.write("ETT SmartFarm")
    time.sleep(2)

    display.write("25.4C Temp")
    time.sleep(2)

    display.write("1234567890ABCDEF")
    time.sleep(2)

    display.clear()
