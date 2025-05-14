# Display.py
from machine import I2C, Pin
import time
import ds3231
from Read_Moisture import read_soil_data

class HT16K33Segment:
    DIGIT_ORDER = [0, 2, 4, 6, 8, 10, 12, 14, 1, 3, 5, 7, 9, 11, 13, 15]

    def __init__(self, i2c, address=0x70):
        self.i2c = i2c
        self.address = address
        self.buffer = bytearray(16)
        self.setup()

    def setup(self):
        self.i2c.writeto(self.address, b'\x21')
        self.i2c.writeto(self.address, b'\x81')
        self.i2c.writeto(self.address, b'\xEF')

    def clear(self):
        self.buffer = bytearray(16)
        self.show()

    def show(self):
        self.i2c.writeto_mem(self.address, 0x00, self.buffer)

    CHAR_MAP = {
        ' ': 0x00, '-': 0x40,
        '0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F,
        '4': 0x66, '5': 0x6D, '6': 0x7D, '7': 0x07,
        '8': 0x7F, '9': 0x6F, 'A': 0x77, 'B': 0x7C, 'C': 0x39, 'D': 0x5E,
        'E': 0x79, 'F': 0x71, 'H': 0x76, 'L': 0x38, 'P': 0x73,
        'S': 0x6D, 'U': 0x3E, 'T': 0x78, 'M': 0x37, 'c': 0x58
    }

    def encode_char(self, char, with_dot=False):
        base = self.CHAR_MAP.get(char.upper(), 0x00)
        return base | 0x80 if with_dot else base

    def print16(self, value):
        value = str(value)
        print(value)
        pos = 0
        i = 0
        while i < len(value) and pos < 16:
            char = value[i]
            if (i + 1 < len(value)) and value[i + 1] == '.':
                self.buffer[self.DIGIT_ORDER[pos]] = self.encode_char(char, with_dot=True)
                i += 2
            else:
                self.buffer[self.DIGIT_ORDER[pos]] = self.encode_char(char, with_dot=False)
                i += 1
            pos += 1
        self.show()

# Setup
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
rtc = ds3231.DS3231(i2c)
disp = HT16K33Segment(i2c)

def read_time():
    y, m, d, dow, h, mi, s = rtc.datetime()
    return "{:02}{:02}".format(h, mi)

TEMP = "0000"
HUMI = "0000"
soil_count = 0

# Main loop
while True:
    time_str = read_time()
    soil = read_soil_data()

    
    SOIL = "{:.1f}C".format(soil['temperature'])
    print("Soil_temp : " + SOIL)
    SOIL = "{:.1f}".format(soil['moisture'])
    print("Soil_humi : " + SOIL)    
    print("PH = {:.1f}".format(soil['ph']))
    print("N = {:.0f}".format(soil['n']))
    print("P = {:.0f}".format(soil['p']))
    print("K = {:.0f}".format(soil['k']))
    

    if soil_count == 1:
        SOIL = "{:.1f}C".format(soil['temperature'])
        soil_count = 0
        #print("Soil_temp : " + SOIL)
    else:
        SOIL = "{:.1f}".format(soil['moisture'])
        soil_count += 1
        #print("Soil_humi : " + SOIL)
    line = time_str + TEMP + HUMI + SOIL
    disp.clear()
    disp.print16(line)
    print("\U0001F552 Displayed:", line)
    time.sleep(5)