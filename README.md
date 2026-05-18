# Smart PC Power Button

Raspberry Pi Pico W that lets Google Home trigger a PC power button press via SinricPro and a relay.

## Wiring

| Pico W Pin    | Connects to              | Purpose                    |
|---------------|--------------------------|----------------------------|
| VBUS (Pin 40) | Relay VCC / +            | 5V relay power             |
| GND (Pin 38)  | Relay GND / −            | Ground                     |
| GP15 (Pin 20) | Relay IN / S             | Power button signal        |
| GP14 (Pin 19) | PWR_LED+ via 1kΩ resistor| Read PC power state        |
| GND (any)     | PWR_LED−                 | Ground for LED sense       |

Relay output → motherboard PWR_SW header:
- **COM** → PWR_SW pin 1
- **NO** (Normally Open) → PWR_SW pin 2

PWR_LED sense → motherboard PWR_LED header:
- **PWR_LED+** → 1kΩ resistor → GP14 (Pin 19)
- **PWR_LED−** → any Pico GND pin

## Setup

1. Copy `main.py` to the root of your Pico W.
2. Install the `sinricpro` library into `/lib` on the Pico W.
3. Link the **Sinric Pro** service in Google Home.
4. Power the Pico W via any 5V USB source — `main.py` runs automatically.

## Usage

Say *"Hey Google, turn on [device name]"* to pulse the power button.

> The relay pulses for 500 ms (simulating a short press). Saying "turn off" is safely ignored — a relay pulse always toggles the PC regardless of direction.

## Relay Logic

If your relay activates in reverse (stays closed by default), swap `relay.value(1)` and `relay.value(0)` in `main.py`.
