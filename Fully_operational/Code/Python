import time, serial, os, requests, cv2, json, re
import paho.mqtt.client as mqtt
from picamera2 import Picamera2
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# -------------------- Serial and Camera Configuration --------------------
LIGHT_PORT, LIGHT_BAUD = '/dev/ttyACM0', 115200
ESP32_PORT, ESP32_BAUD = '/dev/ttyUSB0', 115200
SAVE_IMG, SAVE_JSON = 'Screenshot', 'BackupData'
# -------------------- Google Photos Auth --------------------
CRED_FILE = '/home/mechatronic/Documents/FarmbotCode/client_secret_837120012849-1m7meoaclplf0v8m0133rfkja7bdubtv.apps.googleusercontent.com.json'
TOKEN_FILE, SCOPES = 'token.json', ['https://www.googleapis.com/auth/photoslibrary.appendonly']
# -------------------- LED Configuration --------------------
LEDS = {"red": (5, 4), "green": (2, 3), "blue": (0, 1), "white": (10, 11), "yellow": (7, 6), "violet": (8, 9)}
BRIGHTNESS = {"yellow": 40000, "violet": 40000}
# -------------------- External APIs --------------------
FOG_URL = 'http://192.168.31.254:5000/'
MQTT_BROKER, MQTT_PORT = '161.200.84.240', 1883
MQTT_TOPICS = [f"server/sensor/{k}" for k in ["temperature", "humidity", "light", "pm25"]] + ["server/weather_forecast"]
mqtt_data = {}

send = lambda s, cmd, d=0.05: (s.write((cmd + '\r\n').encode()), time.sleep(d))
# -------------------- MQTT Functions --------------------
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        if msg.topic == "server/weather_forecast":
            d = payload["WeatherForecasts"][0]["forecasts"][0]["data"]
            mqtt_data.update({
                "temperature": d.get("tc"),
                "humidity": d.get("rh"),
                "rain": d.get("rain"),
                "wind_speed": d.get("ws10m"),
                "condition": "Sunny",
                "sunrise": "06:05",
                "sunset": "18:36",
                "time": datetime.now().strftime('%A, %B %d, %Y at %I:%M:%S %p')
            })
        elif "server/sensor/" in msg.topic:
            mqtt_data[f"server_{msg.topic.split('/')[-1]}"] = payload.get("value", "loading..")
    except Exception as e:
        print(f"[MQTT ERROR] Topic: {msg.topic}, Payload: {msg.payload}")
        print(f"[Exception] {e}")

def start_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    for topic in MQTT_TOPICS:
        client.subscribe(topic)
    client.loop_start()
    return client

def fetch_place():
    try:
        response = requests.get(FOG_URL, timeout=5)
        html = response.text

        place_match = re.search(r"<p>(.*?)\s*\{", html)
        latlon_match = re.search(r'"latitude"\s*:\s*([\d.]+),\s*"longitude"\s*:\s*([\d.]+)', html)

        mqtt_data["server_place"] = place_match.group(1).strip() if place_match else "Unknown Place"
        if latlon_match:
            mqtt_data["server_lat"] = latlon_match.group(1)
            mqtt_data["server_lon"] = latlon_match.group(2)
        else:
            mqtt_data["server_lat"] = "Unknown"
            mqtt_data["server_lon"] = "Unknown"

        print(f"✅ Place Loaded: {mqtt_data['server_place']} ({mqtt_data['server_lat']}, {mqtt_data['server_lon']})")

    except Exception as e:
        print(f"❌ Failed to fetch place: {e}")
        mqtt_data["server_place"] = "Unknown Place"
        mqtt_data["server_lat"] = "Unknown"
        mqtt_data["server_lon"] = "Unknown"

send = lambda s, cmd, d=0.05: (s.write((cmd+'\r\n').encode()), time.sleep(d))

def setup_lights(s):
    send(s, "from machine import Pin, PWM; import time")
    for c, (en, pwm) in LEDS.items():
        send(s, f"en{c}=Pin({en},Pin.OUT); pwm{c}=PWM(Pin({pwm})); pwm{c}.freq(20000); en{c}.off(); pwm{c}.duty_u16(0)")

def auth_google():
    creds = None
    if os.path.exists(TOKEN_FILE):
        try: creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except: pass
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try: creds.refresh(Request())
            except: creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'w') as f: f.write(creds.to_json())
    return creds

def upload_photo(creds, path):
    with open(path, 'rb') as f:
        token = requests.post(
            'https://photoslibrary.googleapis.com/v1/uploads',
            headers={
                'Authorization': f'Bearer {creds.token}',
                'Content-type': 'application/octet-stream',
                'X-Goog-Upload-File-Name': os.path.basename(path),
                'X-Goog-Upload-Protocol': 'raw'
            }, data=f.read()).text
    r = requests.post('https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate',
        headers={'Authorization': f'Bearer {creds.token}'},
        json={"newMediaItems": [{"simpleMediaItem": {"uploadToken": token}}]})
    print(f"Uploaded: {os.path.basename(path)}" if r.status_code == 200 else f"Upload failed: {r.text}")

def overlay_text(img):
    font, scale, color, thickness = cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1
    lines = [
        f"Bangkok",
        f"Time: {mqtt_data.get('time', 'loading..')}",
        f"Temperature: {mqtt_data.get('temperature', 'loading..')} Celsius",
        f"Humidity: {mqtt_data.get('humidity', 'loading..')} %",
        f"Rain: {mqtt_data.get('rain', 'loading..')} mm",
        f"Wind: {mqtt_data.get('wind_speed', 'loading..')} m/s",
        f"Condition: {mqtt_data.get('condition', 'loading..')}",
        f"Sunrise: {mqtt_data.get('sunrise', 'loading..')}",
        f"Sunset: {mqtt_data.get('sunset', 'loading..')}",
        f"Server: {mqtt_data.get('server_place', 'loading..')}",
        f"Location: {mqtt_data.get('server_lat', 'loading..')}, {mqtt_data.get('server_lon', 'loading..')}",
        f"Server Temp: {mqtt_data.get('server_temperature', 'loading..')} Celsius",
        f"Server Hum: {mqtt_data.get('server_humidity', 'loading..')} %",
        f"Server Light: {mqtt_data.get('server_light', 'loading..')} lux",
        f"Server PM2.5: {mqtt_data.get('server_pm25', 'loading..')} ug/m^3", 
        f"Edge Temp: {mqtt_data.get('edge_temp', '??')} Celsius",
        f"Edge Hum: {mqtt_data.get('edge_hum', '..')} %",
        f"Edge PH: {mqtt_data.get('edge_ph', '--')}",
        f"Edge N: {mqtt_data.get('edge_n', '--')}",
        f"Edge P: {mqtt_data.get('edge_p', '--')}",
        f"Edge K: {mqtt_data.get('edge_k', '--')}"
    ]
    for idx, line in enumerate(lines):
        cv2.putText(img, line, (10, 30 + idx*20), font, scale, color, thickness)

def capture_with_overlay(cam, color):
    os.makedirs(SAVE_IMG, exist_ok=True)
    os.makedirs(SAVE_JSON, exist_ok=True)
    filename = f"{SAVE_IMG}/{color}_{datetime.now():%Y-%m-%d_%H-%M-%S}.jpg"
    cam.capture_file(filename)
    img = cv2.imread(filename)
    overlay_text(img)
    cv2.imwrite(filename, img)

    json_name = os.path.basename(filename).replace(".jpg", ".json")
    with open(f"{SAVE_JSON}/{json_name}", 'w') as f:
        json.dump(mqtt_data, f, indent=2)

    return filename

def adjust_crop_center(picam2, zoom_factor=2, x_offset=200, y_offset=0, lens_pos=11):
    sensor_w, sensor_h = picam2.sensor_resolution
    crop_w, crop_h = sensor_w // zoom_factor, sensor_h // zoom_factor
    x = max(0, min(sensor_w - crop_w, (sensor_w - crop_w) // 2 + x_offset))
    y = max(0, min(sensor_h - crop_h, (sensor_h - crop_h) // 2 + y_offset))
    picam2.set_controls({
        "ScalerCrop": (x, y, crop_w, crop_h),
        "AfMode": 0,
        "LensPosition": lens_pos,
        "AeEnable": True,
        "AwbEnable": True
    })
    print(f"[DEBUG] ScalerCrop: x={x}, y={y}, w={crop_w}, h={crop_h}")
    time.sleep(2)
    
def capture_color(s, cam, creds, color):
    level = BRIGHTNESS.get(color, 2000)
    send(s, f"en{color}.on(); pwm{color}.duty_u16({level})")
    time.sleep(1)
    filename = capture_with_overlay(cam, color)
    print(f"[Captured]: {filename}")
    upload_photo(creds, filename)
    send(s, f"pwm{color}.duty_u16(0); en{color}.off()")
    time.sleep(0.5)
    
def publish_edge_sensor_data(client):
    try:
        sensors = ['temp', 'hum', 'ph', 'n', 'p', 'k']
        for key in sensors:
            value = mqtt_data.get(f"edge_{key}", None)
            if value is not None:
                topic = f"edge/sensor/{key}"
                client.publish(topic, value)
                print(f"[MQTT] Published {topic} = {value}")
    except Exception as e:
        print(f"[MQTT Publish ERROR] {e}")
    
def read_esp32_serial_values():
    try:
        with serial.Serial(ESP32_PORT, ESP32_BAUD, timeout=2) as ser:
            ser.flushInput()
            lines = []
            start_time = time.time()
            
            while time.time() - start_time < 3:
                if ser.in_waiting:
                    line = ser.readline().decode(errors="ignore").strip()
                    if line:
                        print(f"[ESP32 RAW] {line}")
                        lines.append(line)
                time.sleep(0.1)
            
            for line in lines:
                if "Soil_temp" in line:
                    value = re.search(r"([\d.]+)", line)
                    if value: mqtt_data['edge_temp'] = float(value.group(1))
                elif "Soil_humi" in line:
                    value = re.search(r"([\d.]+)", line)
                    if value: mqtt_data['edge_hum'] = float(value.group(1))
                elif "PH" in line:
                    value = re.search(r"([\d.]+)", line)
                    if value: mqtt_data['edge_ph'] = float(value.group(1))
                elif "N" in line and "Soil" not in line:
                    value = re.search(r"([\d.]+)", line)
                    if value: mqtt_data['edge_n'] = float(value.group(1))
                elif "P" in line and "Soil" not in line:
                    value = re.search(r"([\d.]+)", line)
                    if value: mqtt_data['edge_p'] = float(value.group(1))
                elif "K" in line and "Soil" not in line:
                    value = re.search(r"([\d.]+)", line)
                    if value: mqtt_data['edge_k'] = float(value.group(1))
    except Exception as e:
        print(f"[ESP32 ERROR] {e}")
        
# -------------------- Main Entry Point --------------------
if __name__ == "__main__":
    os.makedirs(SAVE_IMG, exist_ok=True)
    os.makedirs(SAVE_JSON, exist_ok=True)
    ser = serial.Serial(LIGHT_PORT, LIGHT_BAUD, timeout=1)
    time.sleep(2)
    setup_lights(ser)
    client = start_mqtt()
    fetch_place()
    time.sleep(5)

    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={"size": (1280, 720)}))
    picam2.start()
    time.sleep(2)
    
    adjust_crop_center(picam2, zoom_factor=2, x_offset=200)
    creds = auth_google()

    for color in LEDS.keys():
        try:
            read_esp32_serial_values()
            time.sleep(0.5)
            publish_edge_sensor_data(client)
            time.sleep(1)
            send(ser, f"en{color}.on(); pwm{color}.duty_u16({BRIGHTNESS.get(color, 2000)})")
            time.sleep(2)
            filename = capture_with_overlay(picam2, color)
            print(f"[Captured]: {filename}")
            upload_photo(creds, filename)
            send(ser, f"pwm{color}.duty_u16(0); en{color}.off()")
            time.sleep(0.5)
        except Exception as e:
            print(f"Error with {color}: {e}")

    picam2.stop()
    ser.close()
    client.loop_stop()
    print("All tasks completed.")
