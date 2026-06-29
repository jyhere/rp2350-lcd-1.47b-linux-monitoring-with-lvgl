# Changelog

## 1.0 (2026-06-29)

- Complete rewrite: LVGL-based UI (replaced framebuffer)
- ST7789V3 SPI driver (big-endian RGB565, 60 MHz)
- Y-offset 34 fix for panel alignment
- Bar value animation fix (`set_value` + anim=0)
- PC monitoring over USB serial with JSON protocol
- Font sizes 14/16 for better readability
- Color-coded bars (green/orange/red based on load)
- French and English documentation
