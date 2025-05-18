from machine import I2C, Pin
import time

class ETSmartFarmRelay:
    def __init__(self, i2c_bus=0, scl_pin=22, sda_pin=21, address=0x38):
        self.i2c = I2C(i2c_bus, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=100000)
        self.address = address
        self.relay_state = 0xFF  # All relays Off initially
        self._write_state()

    def _write_state(self):
        self.i2c.writeto(self.address, bytes([self.relay_state]))

    def turn_on(self, index: int):
        if 0 <= index <= 7:
            self.relay_state &= ~(1 << index)
            self._write_state()

    def turn_off(self, index: int):
        if 0 <= index <= 7:
            self.relay_state |= (1 << index)
            self._write_state()

    def all_off(self):
        self.relay_state = 0xFF
        self._write_state()

    def all_on(self):
        self.relay_state = 0x00
        self._write_state()

if __name__ == "__main__":
    relay = ETSmartFarmRelay()
    print("Activating relays one by one")
    for i in range(4):  # If only 4 relays used
        relay.turn_on(i)
        print(f"Turn On Relay P{i}")
        time.sleep(1)
        relay.turn_off(i)
        print(f"Turn Off Relay P{i}")

    relay.all_off()
    print("All relays turned Off")
