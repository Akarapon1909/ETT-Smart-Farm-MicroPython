from machine import UART
import time
import struct

class ETSmartFarmSoilSensor:
    def __init__(self, tx=27, rx=26, baudrate=9600, slave_id=1):
        self.uart = UART(2, baudrate=baudrate, tx=tx, rx=rx)
        self.slave_id = slave_id

    def _crc16(self, data):
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc

    def _read_registers(self, start_addr=0, quantity=7):
        req = struct.pack('>BBHH', self.slave_id, 0x03, start_addr, quantity)
        crc = self._crc16(req)
        req += struct.pack('<H', crc)
        self.uart.write(req)
        time.sleep(0.1)
        return self.uart.read()

    def read_all(self) -> dict:
        try:
            data = self._read_registers()
            if data and len(data) >= 17:
                values = struct.unpack('>7H', data[3:-2])
                return {
                    'moisture': values[0] / 10.0,
                    'temperature': values[1] / 10.0,
                    'ph': values[3] / 10.0,
                    'n': values[4],
                    'p': values[5],
                    'k': values[6]
                }
            else:
                print("Invalid data length from sensor.")
        except Exception as e:
            print("Sensor read error:", e)
        return {}

    def read_column(self, name: str):
        return self.read_all().get(name, None)

if __name__ == "__main__":
    sensor = ETSmartFarmSoilSensor()
    while True:
        data = sensor.read_all()
        print("Sensor data:", data)
        time.sleep(5)
