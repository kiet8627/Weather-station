from urequests import post, get, delete
from time import ticks_ms
from bmp180 import BMP180
from machine import Pin, I2C, ADC
from network import WLAN, STA_IF

def check_connection():
    if not sta.isconnected():
        print('Connecting to network...')
        sta.active(True)
        sta.connect("Anh_2.4G", "123456789")
        while not sta.isconnected():
            pass
        print("Connected")
        
        
# -------------------------------------------------- #
sta = WLAN(STA_IF)
HTTP_HEADERS = {'Content-Type': 'application/json'}
THINGSPEAK_WRITE_API_KEY = 'JBO1LIO0SRC8DTE6'
UPDATE_TIME_INTERVAL = 100
last_update = ticks_ms()


# CONNECT WIFI
check_connection()

# BMP180
i2c = I2C(scl = Pin(22), sda = Pin(23))
bmp = BMP180(i2c)

# LDR
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)

# LED & BUZZER
emergency = Pin(15, Pin.OUT)


# MAINLOOP
while True:
    try:
        # EMERGENCY
        check_connection()
        r = get("https://api.thingspeak.com/talkbacks/44846/commands.json?api_key=92EVIWL67NXRMDEZ")
        if len(r.json()) > 0:
            status = 1 if r.json()[0]["command_string"] == "on" else 0
            emergency.value(status)
        if len(r.json()) > 10:
            r = delete("https://api.thingspeak.com/talkbacks/44846/commands.json?api_key=92EVIWL67NXRMDEZ")
            r.close()
        
        if ticks_ms() - last_update >= UPDATE_TIME_INTERVAL:
            # GET DATA
            temperature = bmp.temperature
            pressure = bmp.pressure
            light = ldr.read() / 4095 * 100
            
            # SEND DATA
            check_connection()
            readings = {'field1': temperature, 'field2': light, 'field3': pressure}
            request = post('http://api.thingspeak.com/update?api_key=' + THINGSPEAK_WRITE_API_KEY, json = readings, headers = HTTP_HEADERS)
            request.close()
            print(readings)
            
            last_update = ticks_ms()
            
    except:
        print("Check your devices")
        break