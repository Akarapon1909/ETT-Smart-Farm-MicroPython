from machine import I2C, Pin
import ds3231
import time
from soil_sensor import ETSmartFarmSoilSensor

class ETSmartFarmDisplay:
    DIGIT_ORDER = [0, 2, 4, 6, 8, 10, 12, 14, 1, 3, 5, 7, 9, 11, 13, 15]

    CHAR_MAP = {
        ' ': 0x00, '-': 0x40,
        '0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F,
        '4': 0x66, '5': 0x6D, '6': 0x7D, '7': 0x07,
        '8': 0x7F, '9': 0x6F, 'A': 0x77, 'B': 0x7C, 'C': 0x39, 'D': 0x5E,
        'E': 0x79, 'F': 0x71, 'H': 0x76, 'L': 0x38, 'P': 0x73,
        'S': 0x6D, 'U': 0x3E, 'T': 0x78, 'M': 0x37, 'c': 0x58
    }

    def __init__(self, i2c_bus=0, scl_pin=22, sda_pin=21, address=0x70):
        self.i2c = I2C(i2c_bus, scl=Pin(scl_pin), sda=Pin(sda_pin))
        self.address = address
        self.buffer = bytearray(16)
        self.rtc = ds3231.DS3231(self.i2c)
        self._setup()

    def _setup(self):
        self.i2c.writeto(self.address, b'\x21') 
        self.i2c.writeto(self.address, b'\x81') 
        self.i2c.writeto(self.address, b'\xEF')  

    def clear(self):
        self.buffer = bytearray(16)
        self._show()

    def _show(self):
        self.i2c.writeto_mem(self.address, 0x00, self.buffer)

    def _encode_char(self, char, with_dot=False):
        base = self.CHAR_MAP.get(char.upper(), 0x00)
        return base | 0x80 if with_dot else base

    def print_text(self, text: str):
        text = str(text)
        pos = 0
        i = 0
        while i < len(text) and pos < 16:
            char = text[i]
            if (i + 1 < len(text)) and text[i + 1] == '.':
                self.buffer[self.DIGIT_ORDER[pos]] = self._encode_char(char, with_dot=True)
                i += 2
            else:
                self.buffer[self.DIGIT_ORDER[pos]] = self._encode_char(char)
                i += 1
            pos += 1
        self._show()
        
    def read_time_str(self) -> str:
        y, m, d, dow, h, mi, s = self.rtc.datetime()
        return "{:02}{:02}".format(h, mi)
        
if __name__ == "__main__":
    from soil_sensor import ETSmartFarmSoilSensor
    display = ETSmartFarmDisplay()
    sensor = ETSmartFarmSoilSensor()
    TEMP = "0000"
    HUMI = "0000"
    soil_count = 0

    while True:
        time_str = display.read_time_str()
        try:
            soil = sensor.read_all()
        except Exception as e:
            print("Sensor read error:", e)
            soil = {}

        if soil_count == 1:
            SOIL = "{:.1f}C".format(soil.get('temperature', 0))
            soil_count = 0
            print("Soil_temp :", SOIL)
        else:
            SOIL = "{:.1f}".format(soil.get('moisture', 0))
            soil_count += 1
            print("Soil_humi :", SOIL)

        line = f"{time_str}{TEMP}{HUMI}{SOIL}"[:16]
        display.clear()
        display.print_text(line)
        print("Displayed:", line)
        time.sleep(5)

