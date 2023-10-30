# GLaDOS Potato
A Gif playing Glados Potato firmware written in CircuitPython

https://github.com/vellak8081/GLaDOS-potato-circuitpython/assets/46793137/486d2929-0474-4d25-ac72-7bbf78b0507f

This is intended to run on an RP2040 microcontroller, specifically I used the Waveshare RP2040-Zero.

The files you will need are all inside the 'firmware' directory, except for the library files which you should get from Adafruit.

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

Your lib directory on your microcontroller's CIRCUITPYTHON drive should look something like this: 
![lib](https://github.com/vellak8081/GLaDOS-potato-circuitpython/assets/46793137/a4466b1f-41d4-4d0f-81b4-71cf528edac5)
