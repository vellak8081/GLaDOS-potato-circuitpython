import board
import time
import gc
import os
import struct
import random
import digitalio
import pwmio
import neopixel
import audiomp3
import audiopwmio
import gifio
import busio
import displayio
import terminalio
from adafruit_st7735r import ST7735R
from adafruit_display_text import label


displayio.release_displays()
spi = busio.SPI(clock=board.GP10, MOSI=board.GP11)
display_bus = displayio.FourWire(spi, command=board.GP12, chip_select=board.GP14, reset=board.GP13)
backlight = pwmio.PWMOut(board.GP9, frequency=5000, duty_cycle=0) # turn off the backlight until the display has initialized

display = ST7735R(display_bus, width=128, height=160, colstart=3, rowstart=1)

##### Blank display to prevent showing splash #####
bg = displayio.Group()
display.root_group = bg
color_bitmap = displayio.Bitmap(128, 160, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000 # make the display black

bg_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)

blank_sprite = displayio.TileGrid(color_bitmap,
                               pixel_shader=color_palette,
                               x=0, y=0)
blank = displayio.Group()
blank.append(blank_sprite)

bg.append(bg_sprite)
display.show(bg)

backlight.duty_cycle = 32000 # enable the backlight
display.auto_refresh = False # disable auto refresh
gif = '/logo.gif'
odg = gifio.OnDiskGif(gif)

frame = -1
next_delay = -1
overhead = -1
lastframe = -1

BOOTED = False #flag to indicate if initial boot splash has played
ANIM_STATE = 0 # 0 = playing aperture splash, 1 = aperture splash done, 2 = playing GLaDOS boot sequence, 3 = GLaDOS boot complete
               # Because we have no animations implemented, we're going to pretend that the splash has finished, and sequence from there
               
CURSOR = False
CURSOR_TIME = -1
PROMPT = label.Label(
    font=terminalio.FONT, text="GLaDOS ~ #  ", scale=1
)
PROMPT.anchor_point = (0, 0)
PROMPT.anchored_position = (5, 20)
               
AUDIO_FILES = {
    0: {"file": "audio/hello.mp3", "played": -1},
    1: {"file": "audio/eaten.mp3", "played": -1},
    2: {"file": "audio/murder.mp3", "played": -1},
    3: {"file": "audio/sloclap1.mp3", "played": -1},
    4: {"file": "audio/sloclap2.mp3", "played": -1},
    5: {"file": "audio/bird.mp3", "played": -1},
    6: {"file": "audio/glitch1_1.mp3", "played": -1},
    7: {"file": "audio/glitch1_2.mp3", "played": -1},
    'last': -1  # store last filed played so we don't have to sort the dict all the time.
    }
AUDIO_SILENCE = 5.0 #time between files being played.
GLITCHED = False #flag for glitch effect

audio = audiopwmio.PWMAudioOut(board.GP6) ### set up the PWM audio output and mp3 decoder
mp3 = open(AUDIO_FILES[0]["file"], "rb")
decoder = audiomp3.MP3Decoder(mp3)

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1) ### set up neopixel and blink variables
local_led = True
LOCAL_LED_BLINK_ON_DURATION = 0.12
LOCAL_LED_BLINK_OFF_DURATION = 2.0
LOCAL_LED_BLINK_TIME = -1

eye_led = pwmio.PWMOut(board.GP15, frequency=5000, duty_cycle=65535)
EYE_LED_FADE_DIRECTION = True
EYE_LED_DUTY_CYCLE = 65535
EYE_LED_DC_STEP = 0.125

eye_red_led = digitalio.DigitalInOut(board.GP26)
eye_red_led.direction = digitalio.Direction.OUTPUT
EYE_RED_LED_STATE = 0 # 0 = long off, 1 = 1st flash, 2 = short off 2 = 2nd flash
EYE_RED_LED_BLINK_ON_DURATION = 0.12
EYE_RED_LED_BLINK_OFF_DURATION = 2.4
EYE_RED_LED_BLINK_TIME = -1


while True:
    
    now = time.monotonic()
    
##### play gifs #####
    if ANIM_STATE == 0:
        if frame == -1:
            gif = '/logo.gif'
            odg = gifio.OnDiskGif(gif)
            start = time.monotonic()
            next_delay = odg.next_frame()
            display_bus.send(42, struct.pack(">hh", 2, odg.bitmap.width + 1))
            display_bus.send(43, struct.pack(">hh", 35, odg.bitmap.height + 34))
            display_bus.send(44, odg.bitmap)
            end = time.monotonic()
            overhead = end - start
            lastframe = end
            frame = 0

        if odg.frame_count > frame:
            if now >= lastframe + (next_delay - overhead):
                next_delay = odg.next_frame()
                display_bus.send(42, struct.pack(">hh", 2, odg.bitmap.width + 1))
                display_bus.send(43, struct.pack(">hh", 35, odg.bitmap.height + 34))
                display_bus.send(44, odg.bitmap)
                lastframe = time.monotonic()
                frame = frame + 1
                
        if odg.frame_count == frame:
            if now >= lastframe + (next_delay - overhead):
                ANIM_STATE = 1
                
    if ANIM_STATE == 1:
        frame = -1
        gif = '/boot.gif'
        odg = gifio.OnDiskGif(gif)
        ANIM_STATE = 2
            
    if ANIM_STATE == 2:
        if frame == -1:
            start = time.monotonic()
            next_delay = odg.next_frame()
            display_bus.send(42, struct.pack(">hh", 2, odg.bitmap.width + 1))
            display_bus.send(43, struct.pack(">hh", 3, odg.bitmap.height + 1))
            display_bus.send(44, odg.bitmap)
            end = time.monotonic()
            overhead = end - start
            lastframe = end
            frame = 0

        if odg.frame_count > frame:
            if now >= lastframe + ((next_delay * 2) - overhead):
                next_delay = odg.next_frame()
                display_bus.send(42, struct.pack(">hh", 2, odg.bitmap.width + 1))
                display_bus.send(43, struct.pack(">hh", 3, odg.bitmap.height + 1))
                display_bus.send(44, odg.bitmap)
                lastframe = time.monotonic()
                frame = frame + 1
                
        if odg.frame_count == frame:
            if now >= lastframe + ((next_delay * 2) - overhead):
                ANIM_STATE = 3
                display.root_group = blank
                display.show(blank)
                try:
                    blank.append(PROMPT)
                except:
                    pass
                display.refresh()
                
##### onboard LED blink state machine #####
    if not local_led:
        if now >= LOCAL_LED_BLINK_TIME + LOCAL_LED_BLINK_OFF_DURATION:
            pixel[0] = (0, 128, 0) #blink red
            pixel.write()
            local_led = True
            LOCAL_LED_BLINK_TIME = now
            gc.collect() # we're basically going to use this task as our 'cron' since it always runs
            print(gc.mem_free())
    
    if local_led:
        if now >= LOCAL_LED_BLINK_TIME + LOCAL_LED_BLINK_ON_DURATION:
            pixel[0] = (0, 0, 0) #off
            pixel.write()
            local_led = False
            LOCAL_LED_BLINK_TIME = now

##### eye red led state machine #####
    if ANIM_STATE >= 1:
        if EYE_RED_LED_STATE == 0:
            if now >= EYE_RED_LED_BLINK_TIME + EYE_RED_LED_BLINK_OFF_DURATION:
                eye_red_led.value = False
                EYE_RED_LED_STATE = 1
                EYE_RED_LED_BLINK_TIME = now
            
        if EYE_RED_LED_STATE == 1:
            if now >= EYE_RED_LED_BLINK_TIME + EYE_RED_LED_BLINK_ON_DURATION:
                eye_red_led.value = True
                EYE_RED_LED_STATE = 2
                EYE_RED_LED_BLINK_TIME = now
                
        if EYE_RED_LED_STATE == 2:
            if now >= EYE_RED_LED_BLINK_TIME + EYE_RED_LED_BLINK_ON_DURATION:
                eye_red_led.value = False
                EYE_RED_LED_STATE = 3
                EYE_RED_LED_BLINK_TIME = now
                
        if EYE_RED_LED_STATE == 3:
            if now >= EYE_RED_LED_BLINK_TIME + EYE_RED_LED_BLINK_ON_DURATION:
                eye_red_led.value = True
                EYE_RED_LED_STATE = 0
                EYE_RED_LED_BLINK_TIME = now

##### Eye main LED fade state machine #####
    if ANIM_STATE >= 3: # only after boot animation has played
        if EYE_LED_FADE_DIRECTION:
            if EYE_LED_DUTY_CYCLE <= 60500:
                EYE_LED_FADE_DIRECTION = False
            else:
                EYE_LED_DUTY_CYCLE = EYE_LED_DUTY_CYCLE - EYE_LED_DC_STEP
                eye_led.duty_cycle = int(EYE_LED_DUTY_CYCLE)
        
        if not EYE_LED_FADE_DIRECTION:
            if EYE_LED_DUTY_CYCLE >= 65370:
                EYE_LED_FADE_DIRECTION = True
            else:
                EYE_LED_DUTY_CYCLE = EYE_LED_DUTY_CYCLE + EYE_LED_DC_STEP
                eye_led.duty_cycle = int(EYE_LED_DUTY_CYCLE)
        
##### blinking cursor #####
           
        if CURSOR:
            if now >= CURSOR_TIME + 0.5:
                PROMPT.text = "GLaDOS ~ # _"
                display.refresh()
                CURSOR = False
                CURSOR_TIME = now
                
        if not CURSOR:
            if now >= CURSOR_TIME + 0.5:
                PROMPT.text = "GLaDOS ~ #  "
                display.show(blank)
                display.refresh()
                CURSOR = True
                CURSOR_TIME = now

##### Audio playback #####

        if not audio.playing:
            if AUDIO_FILES['last'] == 6 and GLITCHED == False:
                ANIM_STATE = 0
                frame = -1
                GLITCHED = True
                display.root_group = bg
                display.show(bg)
                display.refresh()
                EYE_RED_LED_STATE = 0 # turn off LEDs and set states
                EYE_RED_LED_BLINK_TIME = -1
                eye_red_led.value = True
                EYE_LED_FADE_DIRECTION = True
                eye_led.duty_cycle = 65535
                
            if AUDIO_FILES[0]["played"] <= 0:
                decoder.file = open(AUDIO_FILES[0]["file"], "rb")
                audio.play(decoder)
                AUDIO_FILES['last'] = 0
                
            else:
                if now >= AUDIO_FILES[AUDIO_FILES['last']]["played"] + AUDIO_SILENCE:
                    if AUDIO_FILES['last'] == 7 and GLITCHED == True:
                        GLITCHED = False
                        
                    if AUDIO_FILES['last'] == 6 and GLITCHED == True:
                        play_file = 7 # always play the second part of the glitch after the first part
                        
                    else:
                        play_file = random.randint(1, len(AUDIO_FILES) - 3) # randomly select one of the files that isn't the 'hello' file or glitch part 2 files

                    decoder.file = open(AUDIO_FILES[play_file]["file"], "rb")
                    audio.play(decoder)
                    AUDIO_FILES['last'] = play_file
                    
        else:
            AUDIO_FILES[AUDIO_FILES['last']]["played"] = now