from ETSmartFarm import Button
import time

btn_reader = I2CButtonReader()

while True:
    states = btn_reader.read_buttons()
    print("Pin states:", states)
    time.sleep(0.5)