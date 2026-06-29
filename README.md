# RP2350 PC Monitor

Monitor PC resource usage (CPU, RAM, network, temperatures) on a Waveshare RP2350-LCD-1.47-B display, powered by LVGL + MicroPython.

![status](https://img.shields.io/badge/status-stable-brightgreen)
![version](https://img.shields.io/badge/version-1.0-blue)

## Hardware

- **Board**: [Waveshare RP2350-LCD-1.47-B](https://www.waveshare.com/rp2350-lcd-1.47-b.htm) (RP2350 + 1.47" 172×320 ST7789V3 LCD)
- **Connection**: USB serial

## Features

- CPU usage (bar + percentage)
- CPU temperature
- RAM usage (bar + percentage)
- Active process count
- Network upload/download speed (KB/s)
- Timestamp display
- Color-coded indicators (CPU/RAM bars change color based on load)
- PC-side auto-reconnect on Pico disconnection

## Project Structure

| File/Dir | Description |
|----------|-------------|
| `main.py` | MicroPython firmware — LVGL UI, LCD driver, serial JSON parser |
| `pc_monitor.py` | PC-side script — gathers system metrics with psutil, sends JSON over serial |
| `lib/lv_utils.py` | LVGL timer helpers (tick + task handler) |
| `images/background-1.png` | Background image for the UI |
| `firmware/` | Custom LVGL+MicroPython firmware build files (see Setup) |

## Custom Firmware

This project requires a **custom MicroPython firmware** built with LVGL bindings.

### Prerequisites

- [lvgl_micropython](https://github.com/lvgl/lvgl_micropython) fork with RP2350 support
- Pico SDK 2.x

### Build

```bash
cd lvgl_micropython
make.py rp2 BOARD=RPI_PICO2
```

The output binary is at `build/lvgl_micropy_RPI_PICO2.uf2`.

### Flash

Hold the **BOOTSEL** button while connecting the Pico 2 via USB, then copy the UF2:

```bash
cp build/lvgl_micropy_RPI_PICO2.uf2 /media/$USER/RPI_RP2/
```

Or use `picotool`:

```bash
picotool load build/lvgl_micropy_RPI_PICO2.uf2 && picotool reboot
```

## Pinout

| LCD Pin | GPIO |
|---------|------|
| DC | 16 |
| CS | 17 |
| SCLK | 18 |
| MOSI | 19 |
| RST | 20 |
| BL  | 21 (PWM) |

Uses **SPI0** at 60 MHz.

## Deployment

### 1. Upload scripts to the board

```bash
mpremote cp main.py :main.py
mpremote cp lib/lv_utils.py :lib/lv_utils.py
```

### 2. Run the PC monitor

```bash
pip install pyserial psutil
python pc_monitor.py
```

## How it works

`pc_monitor.py` polls `psutil` every second and sends a JSON line over USB serial:

```json
{"time":"14:32:01","cpu":"23%","temp":"45.0C","ram":"67%","proc":312,"up":"0.5K","down":"1.2K"}
```

`main.py` parses the JSON and renders it using LVGL on the LCD.

## Technical Details

- Display driver: ST7789V3, 172×320, operated in landscape (320×172) via MADCTL MV=1
- SPI: 60 MHz, big-endian RGB565
- LVGL render mode: `PARTIAL` with 2 draw buffers (1/3 screen each)
- Y-offset of 34 applied in `set_window()` to account for ST7789V3 panel alignment
