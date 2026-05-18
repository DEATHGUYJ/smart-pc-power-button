# Smart PC Power Button

Control your PC's power button with a Google Home voice command. Built on a Raspberry Pi Pico W, a single relay, and [SinricPro](https://sinric.pro).

> "Hey Google, turn on my PC"

---

## How it works

The Pico W connects to SinricPro over WiFi. When Google Home sends a "turn on" command, the Pico closes a relay for 500 ms — identical to pressing the physical power button. A second wire reads the motherboard's PWR_LED header so Google Home always reflects the real power state, even if the PC was turned on or off manually.

---

## Parts

| Item | Notes |
|------|-------|
| Raspberry Pi Pico W | Any revision |
| 5V single-channel relay module | SRD-05VDC-SL-C or equivalent |
| 1kΩ resistor | For PWR_LED sense wire |
| Jumper wires | |

---

## Wiring

### Relay (power button)

| Pico W | Relay module | Purpose |
|--------|-------------|---------|
| VBUS (Pin 40) | VCC / + | 5V power |
| GND (Pin 38) | GND / − | Ground |
| GP15 (Pin 20) | IN / S | Trigger signal |

Connect the relay output to the motherboard **PWR_SW** header:
- Relay **COM** → PWR_SW pin 1
- Relay **NO** → PWR_SW pin 2

### PWR_LED sense (power state feedback)

| Pico W | Motherboard | Notes |
|--------|-------------|-------|
| GP14 (Pin 19) | PWR_LED + | Via 1kΩ resistor |
| Any GND | PWR_LED − | |

The PWR_LED header is usually labelled `PWR_LED`, `PLED`, or `+PW-` on the motherboard, directly next to the PWR_SW header.

---

## Setup

### 1. SinricPro

1. Create a free account at [sinric.pro](https://sinric.pro)
2. Add a new device — type **Switch**
3. Note your **App Key**, **App Secret**, and **Device ID**
4. Link the **Sinric Pro** skill in the Google Home app

### 2. Pico W

1. Flash MicroPython firmware onto the Pico W ([instructions](https://micropython.org/download/RPI_PICO_W/))
2. Open [Thonny](https://thonny.org) and connect to the Pico W
3. Install the SinricPro library into `/lib` on the Pico W
4. Copy `secrets.example.py` to `secrets.py` and fill in your credentials:

```python
WIFI_SSID  = "your-wifi-name"
WIFI_PASS  = "your-wifi-password"
APP_KEY    = "..."
APP_SECRET = "..."
DEVICE_ID  = "..."
```

5. Copy `main.py` and `secrets.py` to the root of the Pico W
6. Reboot — the Pico W runs `main.py` automatically on power-up

---

## LED status

The onboard LED shows connection state at a glance:

| Pattern | Meaning |
|---------|---------|
| Slow blink (1 s) | Connecting to WiFi |
| Fast blink (0.2 s) | WiFi up, connecting to SinricPro |
| Rare brief flash | Ready |

---

## Troubleshooting

**Relay stays closed by default (NC relay)**
Swap `relay.value(1)` and `relay.value(0)` in `main.py`.

**Google Home shows wrong power state**
Check the PWR_LED wiring. The 1kΩ resistor is required — connecting the header directly to GPIO can damage the Pico.

**Device goes offline after a while**
The watchdog timer will reboot the Pico W automatically if the script freezes. If it keeps dropping, check your router's DHCP lease time and assign a static IP to the Pico.

---

## License

MIT
