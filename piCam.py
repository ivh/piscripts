#!/usr/bin/env python3

import picamera
import subprocess
from camcommon import *

import Adafruit_SSD1306
disp = Adafruit_SSD1306.SSD1306_128_64(rst=24)
from PIL import Image, ImageDraw, ImageFont
image = Image.new('1', (disp.width, disp.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()
draw.text((0,30),'Recording & Uploading!', fill=255, font=font)

import RPi.GPIO as GPIO
#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BCM) # Set by display lib already
LAMPON = GPIO.LOW
LAMPOFF = GPIO.HIGH
MOTI = 17 # pin for motion sensor
LAMP = 21 # relay for lamp
CLICK = 20 # empty relay for clicking sound

BOUNCE = 9 # seconds


def record(camera, disp=disp, image=image, duration=BOUNCE, fname=None):
    if not fname:
        fname=getFileName(prefix='cam',suffix='h264')
    dirname,basename = os.path.split(fname)

    GPIO.output(LAMP,LAMPON)
    disp.image(image)
    disp.display()
    camera.start_recording(fname)
    print('Recording to %s ...'%fname, end='', flush=True)

    notify(po, "Motion!", 'Recording %s'%basename,
		url="https://tmy.se/cams/%s.mp4"%basename)

    camera.wait_recording(duration)
    camera.stop_recording()
    GPIO.output(LAMP,LAMPOFF)
    subprocess.call(['MP4Box', '-fps', '15', '-add', fname, '%s.mp4'%fname],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,)
    disp.clear()
    disp.display()
    print(' done.')

try:
    GPIO.setup(MOTI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(LAMP, GPIO.OUT,initial=LAMPOFF)
    GPIO.setup(CLICK, GPIO.OUT,initial=LAMPOFF)

    disp.begin()
    disp.clear()
    disp.display()

    with picamera.PiCamera() as camera:
        #camera.resolution =  (640,480)
        camera.resolution =  (1296,972)
        camera.framerate = 3
        camera.rotation = 180
        camera.start_preview()
        camera.meter_mode='matrix'
        camera.exposure_compensation=6

        GPIO.add_event_detect(MOTI, GPIO.RISING, bouncetime=(BOUNCE+1)*1000,
                    callback=lambda chan: record(camera))
        #GPIO.add_event_callback(MOTI, lambda chan: record(camera))

        while True:
                sleep(0.1)

except KeyboardInterrupt:
    pass

except:
    pass

finally:
    disp.clear()
    disp.display()
    GPIO.cleanup()
