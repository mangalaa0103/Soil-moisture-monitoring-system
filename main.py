import network
import time
import urequests
from machine import ADC, Pin

# ==============================
# WIFI SETTINGS
# ==============================

ssid = "Wokwi-GUEST"
password = ""

# ==============================
# THINGSPEAK SETTINGS
# ==============================

api_key = "JT0LY5V1522WE61I"
server = "http://api.thingspeak.com/update"

# ==============================
# SENSOR CONNECTION
# Potentiometer SIG -> GPIO 34
# ==============================

sensor = ADC(Pin(34))
sensor.atten(ADC.ATTN_11DB)
sensor.width(ADC.WIDTH_12BIT)

# ==============================
# LED CONNECTION
# GPIO 2 -> Resistor -> LED
# LED Cathode -> GND
# ==============================

led = Pin(2, Pin.OUT)

# ==============================
# WIFI CONNECTION
# ==============================

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting to WiFi...")

while not wifi.isconnected():
    time.sleep(0.5)
    print(".", end="")

print()
print("WiFi Connected!")
print("IP Address:", wifi.ifconfig()[0])

# ==============================
# MAIN LOOP
# ==============================

last_time = time.ticks_ms() - 20000

while True:

    # Read potentiometer
    sensor_value = sensor.read()

    # Convert to moisture percentage
    moisture_percent = int(
        (4095 - sensor_value) * 100 / 4095
    )

    moisture_percent = max(
        0, min(100, moisture_percent)
    )

    # Display readings
    print("---------------------------")
    print("Sensor Value:", sensor_value)
    print("Soil Moisture:",
          moisture_percent, "%")

    # LED indication
    if moisture_percent < 40:
        print("Status: DRY")
        led.value(1)
    else:
        print("Status: WET")
        led.value(0)

    # Send data every 20 seconds
    current_time = time.ticks_ms()

    if time.ticks_diff(
        current_time, last_time
    ) >= 20000:

        if wifi.isconnected():

            try:

                url = (
                    server
                    + "?api_key="
                    + api_key
                    + "&field1="
                    + str(moisture_percent)
                )

                response = urequests.get(url)

                print(
                    "ThingSpeak Response:",
                    response.status_code
                )

                if response.status_code == 200:
                    print("Data sent successfully!")

                else:
                    print("ThingSpeak error!")

                response.close()

            except Exception as e:
                print("Error sending data:", e)

        else:
            print("WiFi Disconnected!")

        last_time = current_time

    time.sleep(1)
