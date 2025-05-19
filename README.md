# ETT Smart Farm V1 Plus – Main Controller for Smart Agriculture Projects

ETT Smart Farm V1 Plus is a microcontroller board tailored for Smart Agriculture. It integrates RS485, I²C, RTC, and relay control to support soil sensors (pH, NPK, moisture, temperature, humidity) and is ideal for real-time monitoring and automation in smart farming systems.

---

## Manual & Documentation

- [Documentation From ETT Smart Farm V1 Plus](https://www.etteam.com/productI2C_RS485/ET-SMART-FARM-V1P/index.html)

---

## Step 1: Install Thonny

Download and install the Thonny IDE from:  
https://thonny.org

---

## Step 2: Connect Your ESP32

Plug your ESP32 board into your computer via USB.  
If it's not recognized, install the appropriate USB driver (e.g., CH340 or CP210x).

---

## Step 3: Download MicroPython Firmware

- Get the latest ESP32 firmware from the official site:  
  https://micropython.org/download/esp32

---

## Step 4: Flash the Firmware Using Thonny

1. Open Thonny.
2. Navigate to `Tools > Install or update MicroPython firmware`
3. Select the correct serial port and the `.bin` firmware file
4. Click Install
5. Set up the interpreter via:
   - `Tools > Options > Interpreter`

---

## Step 5: Set Interpreter to MicroPython (ESP32)

- Select the correct Port (e.g., COM3 or /dev/ttyUSB0)
- Click OK

You're ready! Once installed, the MicroPython REPL will appear in Thonny’s shell.  
You can now begin writing and uploading code to your ESP32.

---

## ETT-Smart Farm Wiring Diagram

This wiring diagram shows how to connect all the components.

![Wiring Diagram](images/wiring_diagram.jpg)

### Color Code for Wiring

- Red: Power (VCC, 3.3V/5V/24V)
- Black: Ground (GND)
- Blue: SDA
- Green: SCL
