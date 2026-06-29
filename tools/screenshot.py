import struct
from PIL import Image, ImageDraw, ImageFont

W, H = 320, 172

with open('bg.raw', 'rb') as f:
    raw = f.read()

pixels = bytearray(W * H * 3)
for i in range(0, len(raw), 2):
    px = struct.unpack_from('<H', raw, i)[0]
    r = (px >> 8) & 0xF8
    g = (px >> 3) & 0xFC
    b = (px << 3) & 0xF8
    idx = i // 2
    pixels[idx * 3] = r
    pixels[idx * 3 + 1] = g
    pixels[idx * 3 + 2] = b

img = Image.frombuffer('RGB', (W, H), bytes(pixels), 'raw', 'RGB', 0, 1)

draw = ImageDraw.Draw(img)

def color(hex_val):
    return ((hex_val >> 16) & 0xFF, (hex_val >> 8) & 0xFF, hex_val & 0xFF)

C_BG      = color(0x0A0E1A)
C_TEXT    = color(0xFFFFFF)
C_DIM     = color(0x7070A0)
C_CPU     = color(0x00E676)
C_RAM     = color(0x448AFF)
C_DSK     = color(0xDDA0DD)
C_BAT     = color(0x76FF03)
C_TOP     = color(0x40C4FF)
C_TEMP    = color(0xFF5252)
C_NET_DL  = color(0xFF6B6B)
C_NET_UL  = color(0xFFA726)
C_ACCENT  = color(0x00BCD4)
C_SEP     = color(0x1A2A4A)
C_ORANGE  = color(0xFFA726)
C_BAR_BG  = color(0x0A0E1A)

try:
    f16 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    f14 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    f12 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
except:
    f16 = ImageFont.load_default()
    f14 = f16
    f12 = f16

def bar(im, x, y, w, h, pct, fg_color, bg_color=C_BAR_BG):
    draw.rectangle([x, y, x+w-1, y+h-1], fill=bg_color)
    fill_w = max(1, int(w * pct / 100))
    draw.rectangle([x, y, x+fill_w-1, y+h-1], fill=fg_color)
    draw.rectangle([x, y, x+w-1, y+h-1], outline=color(0x1A1A3A), width=1)

def label(im, x, y, text, fg, font=f16):
    draw.text((x, y), text, fill=fg, font=font)

# Title + time
label(img, 10, 4, "PC MONITOR", C_ACCENT, f16)
label(img, 230, 4, "--:--:--", C_DIM, f16)

# CPU bar
bar(img, 53, 24, 126, 14, 50, C_CPU)
label(img, 10, 22, "CPU", C_DIM, f16)
label(img, 181, 22, "50%", C_CPU, f16)

# RAM bar
bar(img, 53, 48, 126, 14, 60, C_RAM)
label(img, 10, 46, "RAM", C_DIM, f16)
label(img, 183, 46, "60%", C_RAM, f16)

# DSK bar
bar(img, 53, 72, 126, 14, 30, C_DSK)
label(img, 10, 70, "DSK", C_DIM, f16)
label(img, 183, 70, "30%", C_DSK, f16)

# BAT
label(img, 10, 94, "BAT  85%", C_BAT, f16)

# TEMP
label(img, 10, 116, "TEMP  45\u00b0C", C_TEMP, f16)

# TOP
label(img, 10, 138, "TOP  python3", C_TOP, f16)

# DL / UL on same line
label(img, 10, 158, "DL  20.0K/s", C_NET_DL, f14)
label(img, 170, 158, "UL  10.0K/s", C_NET_UL, f14)

img.save('screenshot.png')
print("screenshot.png saved")
