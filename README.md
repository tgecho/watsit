# watsit

Notification server for Raspberry Pi Zero W with a Waveshare 2.13" e-ink display, audio, and LEDs.

POST to `/notify` and it renders text on the display, plays a sound, and blinks an LED.

---

## Hardware

- Raspberry Pi Zero W (or Zero 2 W)
- [Waveshare 2.13inch E-Paper HAT V4](https://www.waveshare.com/2.13inch-e-paper-hat.htm) (250×122px) — plugs directly onto the 40-pin GPIO header
- LED + ~330Ω resistor wired between GPIO 18 (pin 12) and GND (pin 14)
- USB audio adapter (the Pi Zero has no built-in audio out)
- Zero Spy Camera (connects via the Pi Zero's CSI ribbon cable)

---

## Raspberry Pi setup from scratch

### 1. Flash OS

Use **Raspberry Pi OS Lite (64-bit, Bookworm)** — no desktop needed. Flash with [Raspberry Pi Imager](https://www.raspberrypi.com/software/). In the imager's advanced settings, configure:

- hostname (e.g. `watsit.local`)
- your Wi-Fi SSID and password
- SSH enabled with your public key

### 2. First boot — system packages

SSH in and update:

```bash
sudo apt update && sudo apt upgrade -y
```

Install audio tools, fonts, and the camera library:

```bash
sudo apt install -y mpg123 alsa-utils fonts-dejavu-core python3-picamera2
```

`aplay` (for WAV playback) is included in `alsa-utils`. `fonts-dejavu-core` provides the font used for display rendering. `python3-picamera2` is the camera library — it's not on PyPI so it must be installed via apt.

### 3. Enable SPI and camera

Both are off by default. Run `sudo raspi-config` and enable:

- **Interface Options → SPI → Yes** (e-ink display)
- **Interface Options → Camera → Yes** (spy camera)

Reboot when prompted:

```bash
sudo reboot
```

### 4. Configure USB audio

Plug in your USB audio adapter, then verify it's detected:

```bash
aplay -l
```

You should see it listed as a card (e.g. `card 1`). To make it the default, create `/etc/asound.conf`:

```
defaults.pcm.card 1
defaults.ctl.card 1
```

Replace `1` with whatever card number your adapter shows. Test with:

```bash
aplay /usr/share/sounds/alsa/Front_Left.wav
```

### 5. Install Python 3.12

Raspberry Pi OS Bookworm ships with Python 3.11. Install `uv`, which can fetch and manage Python versions:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv python install 3.12
```

### 6. Install the Waveshare e-ink driver

The `waveshare_epd` library is not on PyPI — install it from source:

```bash
git clone https://github.com/waveshareteam/e-Paper.git
pip install ./e-Paper/RaspberryPi_JetsonNano/python
```

### 7. Clone and install watsit

```bash
git clone <repo-url> ~/watsit
cd ~/watsit
uv sync
```

---

## Running

**Mock mode** (default, no hardware required — saves a preview PNG instead of driving the display):

```bash
uv run python server.py
```

**Real hardware mode:**

```bash
MOCK_HARDWARE=0 uv run python server.py
```

The server listens on port 6000.

---

## API

```bash
# Text only
curl -X POST http://watsit.local:6000/notify \
  -H "Content-Type: application/json" \
  -d '{"text": "hello"}'

# With sound and LED blink
curl -X POST http://watsit.local:6000/notify \
  -H "Content-Type: application/json" \
  -d '{"text": "alert", "sound": "chord", "leds": true}'
```

`sound` can be `true` (plays `chord.wav`) or any filename stem from the `sounds/` directory.

```bash
# Snapshot from camera
curl http://watsit.local:6000/snapshot --output snap.jpg
```

---

## Run on boot with systemd

Create `/etc/systemd/system/watsit.service`:

```ini
[Unit]
Description=watsit notification server
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/watsit
Environment=MOCK_HARDWARE=0
ExecStart=/home/pi/.local/bin/uv run python server.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable watsit
sudo systemctl start watsit
```

Check logs:

```bash
journalctl -u watsit -f
```

---

## Development (non-Pi)

With `MOCK_HARDWARE=1` (the default), no hardware imports happen. The server runs normally — display output is saved to `display_preview.png`, audio and LED actions print to stdout.
