from ETSmartFarm import Display
import time

if __name__ == "__main__":
    display = Display()
    display.write("TEMP 25.3C")
    time.sleep(2)
    display.write("MOIS 45.8%")
    time.sleep(2)
    display.clear()
