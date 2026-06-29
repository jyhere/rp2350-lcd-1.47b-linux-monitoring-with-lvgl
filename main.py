import sys
import select
import json
import lvgl as lv
from machine import Pin, SPI, PWM
import time

from lib.lv_utils import event_loop

DC = 16
CS = 17
SCLK = 18
MOSI = 19
RST = 20
BL = 21
FLIPPED = True

class LCD_1inch47:
    def __init__(self):
        self.width = 320
        self.height = 172
        self.cs = Pin(CS, Pin.OUT)
        self.rst = Pin(RST, Pin.OUT)
        self.cs(1)
        self.spi = SPI(0, 60_000_000, polarity=0, phase=0,
                       sck=Pin(SCLK), mosi=Pin(MOSI), miso=None)
        self.dc = Pin(DC, Pin.OUT)
        self.dc(1)
        self.init_display()

    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        self.rst(1)
        self.rst(0)
        self.rst(1)

        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A)
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x13)

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F)

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xF0)
        self.write_data(0x00)
        self.write_data(0x04)
        self.write_data(0x04)
        self.write_data(0x05)
        self.write_data(0x29)
        self.write_data(0x33)
        self.write_data(0x3E)
        self.write_data(0x38)
        self.write_data(0x12)
        self.write_data(0x12)
        self.write_data(0x28)
        self.write_data(0x30)

        self.write_cmd(0xE1)
        self.write_data(0xF0)
        self.write_data(0x07)
        self.write_data(0x0A)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x07)
        self.write_data(0x28)
        self.write_data(0x33)
        self.write_data(0x3E)
        self.write_data(0x36)
        self.write_data(0x14)
        self.write_data(0x14)
        self.write_data(0x29)
        self.write_data(0x23)

        self.write_cmd(0x21)
        self.write_cmd(0x11)
        self.write_cmd(0x29)

        if FLIPPED:
            self.write_cmd(0x36)
            self.write_data(0xB0)

    def set_window(self, x1, y1, x2, y2):
        self.write_cmd(0x2A)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xFF)
        self.write_data(x2 >> 8)
        self.write_data(x2 & 0xFF)
        self.write_cmd(0x2B)
        y_ofs = 34
        self.write_data((y1 + y_ofs) >> 8)
        self.write_data((y1 + y_ofs) & 0xFF)
        self.write_data((y2 + y_ofs) >> 8)
        self.write_data((y2 + y_ofs) & 0xFF)
        self.write_cmd(0x2C)

    def write_pixels(self, data):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)


pwm = PWM(Pin(BL))
pwm.freq(1000)
pwm.duty_u16(32768)

lcd = LCD_1inch47()

lv.init()

color_format = lv.COLOR_FORMAT.RGB565
buf_size = lcd.width * lcd.height // 3
buf1 = lv.draw_buf_create(lcd.width, lcd.height // 3, color_format, 0)
buf2 = lv.draw_buf_create(lcd.width, lcd.height // 3, color_format, 0)

disp = lv.display_create(lcd.width, lcd.height)
disp.set_color_format(color_format)
disp.set_draw_buffers(buf1, buf2)
disp.set_render_mode(lv.DISPLAY_RENDER_MODE.PARTIAL)

# RGB565 byte swap buffer (pre-allocated for performance)
_swap_buf = bytearray(lcd.width * lcd.height // 3 * 2)

def disp_flush(disp_drv, area, color_p):
    w = area.x2 - area.x1 + 1
    h = area.y2 - area.y1 + 1
    size = w * h * 2

    if hasattr(color_p, '__dereference__'):
        data = color_p.__dereference__(size)
    else:
        data = bytes(color_p)

    # ST7789V3 expects big-endian RGB565, LVGL uses native (little-endian)
    global _swap_buf
    needed = size
    if needed > len(_swap_buf):
        _swap_buf = bytearray(needed)
    buf = _swap_buf[:needed]
    for i in range(0, needed, 2):
        buf[i] = data[i + 1]
        buf[i + 1] = data[i]

    lcd.set_window(area.x1, area.y1, area.x2, area.y2)
    lcd.write_pixels(buf)
    disp_drv.flush_ready()

disp.set_flush_cb(disp_flush)

event_loop()

C_BG = lv.color_hex(0x0A0E1A)
C_TEXT = lv.color_hex(0xFFFFFF)
C_DIM = lv.color_hex(0x7070A0)
C_CPU = lv.color_hex(0x00E676)
C_RAM = lv.color_hex(0x448AFF)
C_DSK = lv.color_hex(0xDDA0DD)
C_BAT = lv.color_hex(0x76FF03)
C_TOP = lv.color_hex(0x40C4FF)
C_TEMP = lv.color_hex(0xFF5252)
C_NET_DL = lv.color_hex(0xFF6B6B)
C_NET_UL = lv.color_hex(0xFFA726)
C_ACCENT = lv.color_hex(0x00BCD4)
C_SEP = lv.color_hex(0x1A2A4A)
C_ORANGE = lv.color_hex(0xFFA726)

scr = lv.screen_active()
scr.set_style_bg_color(C_BG, 0)

with open('bg.raw', 'rb') as f:
    bg_data = f.read()
bg_dsc = lv.image_dsc_t()
bg_dsc.header.w = 320
bg_dsc.header.h = 172
bg_dsc.header.cf = lv.COLOR_FORMAT.RGB565
bg_dsc.data_size = len(bg_data)
bg_dsc.data = bg_data
bg_img = lv.image(scr)
bg_img.set_src(bg_dsc)
bg_img.set_pos(0, 0)
bg_img.move_background()

label_title = lv.label(scr)
label_title.set_text("PC MONITOR")
label_title.set_pos(10, 4)
label_title.set_style_text_color(C_ACCENT, 0)
label_title.set_style_text_font(lv.font_montserrat_16, 0)

label_time = lv.label(scr)
label_time.set_text("--:--:--")
label_time.set_pos(230, 4)
label_time.set_style_text_color(C_DIM, 0)
label_time.set_style_text_font(lv.font_montserrat_16, 0)

st_cpu_ind = lv.style_t()
st_cpu_ind.init()
st_cpu_ind.set_bg_color(C_CPU)
st_cpu_ind.set_radius(2)

st_ram_ind = lv.style_t()
st_ram_ind.init()
st_ram_ind.set_bg_color(C_RAM)
st_ram_ind.set_radius(2)

bar_cpu = lv.bar(scr)
bar_cpu.set_size(126, 14)
bar_cpu.set_pos(53, 24)
bar_cpu.set_range(0, 100)
bar_cpu.set_style_bg_color(C_BG, 0)
bar_cpu.set_style_border_width(0, 0)
bar_cpu.set_style_radius(2, 0)
bar_cpu.set_style_pad_all(0, 0)

bar_ram = lv.bar(scr)
bar_ram.set_size(126, 14)
bar_ram.set_pos(53, 48)
bar_ram.set_range(0, 100)
bar_ram.set_style_bg_color(C_BG, 0)
bar_ram.set_style_border_width(0, 0)
bar_ram.set_style_radius(2, 0)
bar_ram.set_style_pad_all(0, 0)

st_dsk_ind = lv.style_t()
st_dsk_ind.init()
st_dsk_ind.set_bg_color(C_DSK)
st_dsk_ind.set_radius(2)

bar_dsk = lv.bar(scr)
bar_dsk.set_size(126, 14)
bar_dsk.set_pos(53, 72)
bar_dsk.set_range(0, 100)
bar_dsk.set_style_bg_color(C_BG, 0)
bar_dsk.set_style_border_width(0, 0)
bar_dsk.set_style_radius(2, 0)
bar_dsk.set_style_pad_all(0, 0)

label_cpu = lv.label(scr)
label_cpu.set_text("CPU")
label_cpu.set_pos(10, 22)
label_cpu.set_style_text_color(C_DIM, 0)
label_cpu.set_style_text_font(lv.font_montserrat_16, 0)

label_cpu_val = lv.label(scr)
label_cpu_val.set_text("0%")
label_cpu_val.set_pos(181, 22)
label_cpu_val.set_style_text_color(C_CPU, 0)
label_cpu_val.set_style_text_font(lv.font_montserrat_16, 0)

label_ram = lv.label(scr)
label_ram.set_text("RAM")
label_ram.set_pos(10, 46)
label_ram.set_style_text_color(C_DIM, 0)
label_ram.set_style_text_font(lv.font_montserrat_16, 0)

label_ram_val = lv.label(scr)
label_ram_val.set_text("0%")
label_ram_val.set_pos(183, 46)
label_ram_val.set_style_text_color(C_RAM, 0)
label_ram_val.set_style_text_font(lv.font_montserrat_16, 0)

label_dsk = lv.label(scr)
label_dsk.set_text("DSK")
label_dsk.set_pos(10, 70)
label_dsk.set_style_text_color(C_DIM, 0)
label_dsk.set_style_text_font(lv.font_montserrat_16, 0)

label_dsk_val = lv.label(scr)
label_dsk_val.set_text("0%")
label_dsk_val.set_pos(183, 70)
label_dsk_val.set_style_text_color(C_DSK, 0)
label_dsk_val.set_style_text_font(lv.font_montserrat_16, 0)

label_bat = lv.label(scr)
label_bat.set_text("BAT  ---")
label_bat.set_pos(10, 94)
label_bat.set_style_text_color(C_BAT, 0)
label_bat.set_style_text_font(lv.font_montserrat_16, 0)

label_top = lv.label(scr)
label_top.set_text("TOP  ---------")
label_top.set_pos(10, 138)
label_top.set_style_text_color(C_TOP, 0)
label_top.set_style_text_font(lv.font_montserrat_16, 0)

label_temp = lv.label(scr)
label_temp.set_text("TEMP  --\u00b0C")
label_temp.set_pos(10, 116)
label_temp.set_style_text_color(C_TEMP, 0)
label_temp.set_style_text_font(lv.font_montserrat_16, 0)

label_net_dl = lv.label(scr)
label_net_dl.set_text("DL  ---.-K/s")
label_net_dl.set_pos(10, 158)
label_net_dl.set_style_text_color(C_NET_DL, 0)
label_net_dl.set_style_text_font(lv.font_montserrat_14, 0)

label_net_ul = lv.label(scr)
label_net_ul.set_text("UL  ---.-K/s")
label_net_ul.set_pos(170, 158)
label_net_ul.set_style_text_color(C_NET_UL, 0)
label_net_ul.set_style_text_font(lv.font_montserrat_14, 0)

print("LVGL PC Monitor initialized, listening...")

while True:
    if select.select([sys.stdin], [], [], 0.05)[0]:
        line = sys.stdin.readline().strip()
        try:
            stats = json.loads(line)

            label_time.set_text(stats['time'])

            cpu_pct = float(stats['cpu'].rstrip('%'))
            label_cpu_val.set_text(stats['cpu'])
            bar_cpu.set_value(int(cpu_pct), 0)

            ram_pct = float(stats['ram'].rstrip('%'))
            label_ram_val.set_text(stats['ram'])
            bar_ram.set_value(int(ram_pct), 0)

            dsk_pct = float(stats['disk'].rstrip('%'))
            label_dsk_val.set_text(stats['disk'])
            bar_dsk.set_value(int(dsk_pct), 0)

            label_bat.set_text("BAT  " + stats['battery'])
            label_top.set_text("TOP  " + stats['top'])
            label_temp.set_text("TEMP  " + stats['temp'])

            color = C_CPU if cpu_pct < 70 else (C_ORANGE if cpu_pct < 90 else C_RAM)
            label_cpu_val.set_style_text_color(color, 0)
            st_cpu_ind.set_bg_color(color)
            bar_cpu.remove_style(st_cpu_ind, lv.PART.INDICATOR)
            bar_cpu.add_style(st_cpu_ind, lv.PART.INDICATOR)

            color = C_RAM if ram_pct < 80 else (C_ORANGE if ram_pct < 95 else C_RAM)
            label_ram_val.set_style_text_color(color, 0)
            st_ram_ind.set_bg_color(color)
            bar_ram.remove_style(st_ram_ind, lv.PART.INDICATOR)
            bar_ram.add_style(st_ram_ind, lv.PART.INDICATOR)

            color = C_DSK if dsk_pct < 80 else (C_ORANGE if dsk_pct < 95 else C_RAM)
            label_dsk_val.set_style_text_color(color, 0)
            st_dsk_ind.set_bg_color(color)
            bar_dsk.remove_style(st_dsk_ind, lv.PART.INDICATOR)
            bar_dsk.add_style(st_dsk_ind, lv.PART.INDICATOR)

            label_net_dl.set_text("DL  " + stats['down'] + "/s")
            label_net_ul.set_text("UL  " + stats['up'] + "/s")

        except Exception:
            pass
