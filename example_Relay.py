
from ETSmartFarm import Relay
from machine import I2C, Pin
import time

if __name__ == "__main__":
    i2c = I2C(0, scl=Pin(22), sda=Pin(21))

    relay = Relay(i2c)

    relay.on1()
    time.sleep(1)
    relay.on2()
    time.sleep(1)
    relay.on3()
    time.sleep(1)
    relay.on4()
    time.sleep(1)

    relay.off_all()
    print("All relays turned off.")
