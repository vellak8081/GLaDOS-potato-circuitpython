# GLaDOS Potato
A Gif playing Glados Potato firmware written in CircuitPython

This is intended to run on an RP2040 microcontroller, specifically I used the Waveshare RP2040-Zero.

To be able to play Gifs, you'll need to use at least CircuitPython 8.x release.

Feel free to use a different display and adapt the code for that display controller, but the gifs are 128x64 and 128x128 pixels, so you'll need one at least that size.
Color LCDs are preferred because otherwise the text dithering/hinting and fade effects look weird.

A number of libraries are required for this to work as written.

For the display:
* adafruit_ST7735r
* adafruit_display_text

For the built in neopixel on the Waveshare RP2040-Zero:
* neopixel
* adafruit_pixelbuf
* adafruit_rgbled
* adafruit_bitbangio
