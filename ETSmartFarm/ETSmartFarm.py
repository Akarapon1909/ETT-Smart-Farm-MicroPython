from machine import I2C, Pin, UART, ADC
from umqtt.simple import MQTTClient
import time, struct, network

class Wifi:
    def __init__(self, ssid, password, mqtt_broker, mqtt_port, mqtt_client, mqtt_user, mqtt_pass, topic_sub=None, callback=None):
        self.ssid = ssid
        self.password = password
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_client = mqtt_client
        self.mqtt_user = mqtt_user
        self.mqtt_pass = mqtt_pass
        self.topic_sub = topic_sub
        self.callback = callback
        self.client = None
        
    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print("Connecting to WiFi...")
            wlan.connect(self.ssid, self.password)
            retry = 0
            while not wlan.isconnected() and retry < 10:
                time.sleep(2)
                retry += 1
                print("Retry", retry)
        print("WiFi connected:", wlan.ifconfig())
        
    def connect_mqtt(self):
        self.client = MQTTClient(self.mqtt_client, self.mqtt_broker, port=self.mqtt_port,
                                 user=self.mqtt_user, password=self.mqtt_pass)
        if self.callback:
            self.client.set_callback(self.callback)

        print("Connecting to MQTT broker...")
        self.client.connect()
        print("MQTT connected.")

        if self.topic_sub:
            self.client.subscribe(self.topic_sub)
            print("Subscribed to:", self.topic_sub)

    def check_msg(self):
        if self.client:
            self.client.check_msg()

    def publish(self, topic, msg):
        if self.client:
            self.client.publish(topic, msg)
            
    def auto_loop(self, publish_callback, interval_ms=5000):
        last = time.ticks_ms()
        while True:
            if not self.client:
                self.connect_mqtt()

            self.check_msg()

            now = time.ticks_ms()
            if time.ticks_diff(now, last) > interval_ms:
                publish_callback()
                last = now

            time.sleep(0.5)

            try:
                self.client.ping()
            except:
                print("MQTT disconnected. Reconnecting...")
                break

class Relay:
    def __init__(self, i2c, address=0x38):
        self.i2c = i2c
        self.address = address
        self.state = 0xFF
        self._write_state()
        
    def _write_state(self):
        self.i2c.writeto(self.address, bytes([self.state]))
    
    def _set(self, ch, on):
        if not 0 <= ch <= 7:
            raise ValueError("Channel must be 0–7")
        if on:
            self.state &= ~(1 << ch)  
        else:
            self.state |= (1 << ch)   
        self._write_state()

    def on(self, ch): self._set(ch, True)
    def off(self, ch): self._set(ch, False)

    def on1(self): self.on(0)
    def on2(self): self.on(1)
    def on3(self): self.on(2)
    def on4(self): self.on(3)

    def off1(self): self.off(0)
    def off2(self): self.off(1)
    def off3(self): self.off(2)
    def off4(self): self.off(3)

    def off_all(self):
        self.state = 0xFF
        self._write_state()
    
class Display:
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
    
    def print(self, text: str):
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
        
class SHT31:
    def __init__(self, i2c, addr=0x44):
        if i2c is None:
            raise ValueError('I2C object is required')
        self._i2c = i2c
        self._addr = addr

    def _send_command(self, command):
        self._i2c.writeto(self._addr, command)

    def _read_data(self, num_bytes):
        return self._i2c.readfrom(self._addr, num_bytes)

    def _read_raw_data(self):
        self._send_command(b'\x24\x00')
        time.sleep_ms(15)
        data = self._read_data(6)
        if len(data) != 6:
            raise RuntimeError("Failed to read data from SHT31 sensor")
        temp_raw = data[0] << 8 | data[1]
        hum_raw = data[3] << 8 | data[4]
        return temp_raw, hum_raw

    def temperature(self):
        temp_raw, _ = self._read_raw_data()
        return -45 + (175 * (temp_raw / 65535.0))

    def humidity(self):
        _, hum_raw = self._read_raw_data()
        return 100 * (hum_raw / 65535.0)
    
class RS485:
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
    
class BH1750:
    PWR_DOWN = 0x00
    PWR_ON = 0x01
    RESET = 0x07
    CONT_HIRES_1 = 0x10

    def __init__(self, i2c, address=0x23):
        self.i2c = i2c
        self.address = address
        self._configure()

    def _configure(self):
        try:
            self.i2c.writeto(self.address, bytes([self.PWR_ON]))
            time.sleep_ms(10)
            self.i2c.writeto(self.address, bytes([self.RESET]))
            time.sleep_ms(10)
            self.i2c.writeto(self.address, bytes([self.CONT_HIRES_1]))
            time.sleep_ms(180)
        except Exception as e:
            print("BH1750 configuration error:", e)

    def read_lux(self):
        try:
            data = self.i2c.readfrom(self.address, 2)
            result = (data[0] << 8) | data[1]
            return result / 1.2  # Convert to Lux
        except Exception as e:
            print("BH1750 read error:", e)
            return None

class Button:
    def __init__(self, i2c_id=0, scl=22, sda=21, address=0x3B):
        self.i2c = I2C(i2c_id, scl=Pin(scl), sda=Pin(sda), freq=100_000)
        self.address = address
        
        print("I2C Scan:", self.i2c.scan())
        self.i2c.writeto(self.address, bytes([0xFF]))
        
    def read_buttons(self):
        try:
            data = self.i2c.readfrom(self.address, 1)
            pin_states = data[0]

            return {
                "P1": (pin_states >> 7) & 1,
                "P2": (pin_states >> 5) & 1,
                "P3": (pin_states >> 3) & 1,
                "P4": (pin_states >> 1) & 1
            }
        except Exception as e:
            print("Read error:", e)
            return {"P1": 1, "P2": 1, "P3": 1, "P4": 1}