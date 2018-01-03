#!/usr/bin/env python3

import picamera
import subprocess
from camcommon import *

import RPi.GPIO as GPIO
#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
MOTI = 11 # pin for motion sensor
GPIO.setup(MOTI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
LAMP = 40 # relay for lamp
CLICK = 38 # empty relay for clicking sound
LAMPON = GPIO.LOW
LAMPOFF = GPIO.HIGH
GPIO.setup(LAMP, GPIO.OUT,initial=LAMPOFF)
GPIO.setup(CLICK, GPIO.OUT,initial=LAMPOFF)

BOUNCE = 10 # seconds

def record(camera, duration=BOUNCE, fname=None):
    if not fname:
        fname=getFileName(prefix='cam',suffix='h264')
    dirname,basename = os.path.split(fname)

    camera.start_recording(fname)
    print('Recording to %s ...'%fname, end='', flush=True)

    notify(po, "Motion!", 'Recording %s'%basename,
		url="https://tmy.se/cams/%s.mp4"%basename)

    camera.wait_recording(duration)
    camera.stop_recording()
    subprocess.call(['MP4Box', '-fps', '15', '-add', fname, '%s.mp4'%fname],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,)
    print(' done.')

def light_click(duration=BOUNCE):
    GPIO.output(LAMP,LAMPON)
    Hz = 2
    interv = 1.0/ Hz / duration
    for i in range(Hz*duration):
        GPIO.output(CLICK,LAMPON)
        sleep(interv/2)
        GPIO.output(CLICK,LAMPOFF)
        sleep(interv/2)
    GPIO.output(LAMP,LAMPOFF)


# main()

try:
    with picamera.PiCamera() as camera:
        #camera.resolution =  (640,480)
        camera.resolution =  (1296,972)
        camera.framerate = 3
        camera.rotation = 180
        camera.start_preview()
        camera.meter_mode='matrix'
        camera.exposure_compensation=9

        GPIO.add_event_detect(MOTI, GPIO.RISING, bouncetime=BOUNCE*1000 +100)
        GPIO.add_event_callback(MOTI, lambda chan: GPIO.output(LAMP,LAMPON))
        GPIO.add_event_callback(MOTI, lambda chan: record(camera))
        GPIO.add_event_callback(MOTI, lambda chan: GPIO.output(LAMP,LAMPOFF))
        #GPIO.add_event_callback(MOTI, lambda chan: light_click())
        #GPIO.add_event_detect(MOTI, GPIO.RISING, bouncetime=(BOUNCE+1)*1000,
        #    callback=lambda chan: record(camera))

        while True:
                sleep(0.1)

except KeyboardInterrupt:
    pass

except:
    pass

finally:
    GPIO.cleanup()
