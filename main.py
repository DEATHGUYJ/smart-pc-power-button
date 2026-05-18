import network
import uasyncio as asyncio
from machine import Pin, WDT
from sinricpro import SinricPro
from sinricpro.devices.sinricpro_switch import SinricProSwitch
from secrets import WIFI_SSID, WIFI_PASS, APP_KEY, APP_SECRET, DEVICE_ID

PULSE_MS        = 500   # relay close duration in ms
RECONNECT_S     = 10    # seconds between WiFi reconnect attempts
LED_POLL_MS     = 500   # PWR_LED sample interval
DEBOUNCE_TICKS  = 3     # stable samples required before accepting state change (3 × 500ms = 1.5s)

# --- HARDWARE ---
relay  = Pin(15, Pin.OUT,  value=0)
led    = Pin("LED", Pin.OUT, value=0)
pc_led = Pin(14, Pin.IN, Pin.PULL_DOWN)  # PWR_LED+ via 1kΩ → GP14, PWR_LED− → GND

wdt = WDT(timeout=8000)  # reboot if main loop freezes for >8s

# --- LED STATUS ---
# Patterns: (on_ms, off_ms) — None means solid on
_led_pattern = (1000, 1000)  # default: slow blink = no WiFi

async def run_status_led():
    while True:
        on_ms, off_ms = _led_pattern
        led.value(1)
        await asyncio.sleep_ms(on_ms)
        led.value(0)
        await asyncio.sleep_ms(off_ms)

def set_led(pattern):
    global _led_pattern
    _led_pattern = pattern

LED_NO_WIFI    = (1000, 1000)   # slow blink
LED_NO_SINRIC  = (200,  200)    # fast blink
LED_READY      = (50,   2950)   # rare brief flash = idle/ready
LED_PULSE      = (50,   50)     # rapid flash during relay pulse (handled inline)

# --- SINRIC PRO CALLBACK ---
async def on_power_state(device_id: str, state: bool):
    if not state:
        return True

    if pc_led.value() == 1:
        print("PC is already on — skipping pulse.")
        return True

    print("Pulsing power button...")
    try:
        relay.value(1)
        led.value(1)
        await asyncio.sleep_ms(PULSE_MS)
    finally:
        relay.value(0)
        led.value(0)

    print("Done.")
    return True

# --- PWR_LED MONITOR (with debounce) ---
async def monitor_pc_power(switch_device):
    last_reported = None
    pending_state = None
    stable_count  = 0

    while True:
        current = pc_led.value() == 1

        if current == pending_state:
            stable_count += 1
        else:
            pending_state = current
            stable_count  = 1

        if stable_count >= DEBOUNCE_TICKS and current != last_reported:
            last_reported = current
            print("PC power state:", "ON" if current else "OFF")
            try:
                switch_device.send_power_state_event(current)
            except Exception as e:
                print("Failed to report state:", e)

        await asyncio.sleep_ms(LED_POLL_MS)

# --- WIFI ---
async def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm=0xa11140)  # disable power-save

    while True:
        if wlan.isconnected():
            await asyncio.sleep(5)
            continue

        set_led(LED_NO_WIFI)
        print(f"Connecting to {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASS)

        for _ in range(30):
            if wlan.isconnected():
                print("WiFi connected:", wlan.ifconfig()[0])
                break
            await asyncio.sleep(1)
        else:
            print("WiFi timeout, retrying...")
            wlan.disconnect()
            await asyncio.sleep(RECONNECT_S)

# --- MAIN ---
async def main():
    asyncio.create_task(run_status_led())
    asyncio.create_task(connect_wifi())

    wlan = network.WLAN(network.STA_IF)
    while not wlan.isconnected():
        wdt.feed()
        await asyncio.sleep(1)

    set_led(LED_NO_SINRIC)

    client    = SinricPro()
    my_switch = SinricProSwitch(DEVICE_ID)
    my_switch.on_power_state(on_power_state)
    client.add_device(my_switch)

    print("Starting SinricPro...")
    client.start(APP_KEY, APP_SECRET)

    set_led(LED_READY)
    asyncio.create_task(monitor_pc_power(my_switch))

    while True:
        wdt.feed()
        await asyncio.sleep(1)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    relay.value(0)
    print("Stopped.")
