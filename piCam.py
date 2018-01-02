#!/usr/bin/env python3

import picamera
import subprocess
from camcommon import *

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
MOTI = 40 # last pin is motion sensor
GPIO.setup(MOTI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
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
    subprocess.call(['MP4Box', '-fps', '15', '-add', fname, '%s.mp4'%fname])
    print(' done.')


with picamera.PiCamera() as camera:
    camera.resolution =  (640,480)
    #camera.resolution =  (1296,972)
    camera.framerate = 5
    camera.rotation = 180
    camera.start_preview()
    camera.meter_mode='matrix'
    camera.exposure_compensation=9

    GPIO.add_event_detect(MOTI, GPIO.RISING, bouncetime=(BOUNCE+1)*1000,
        callback=lambda chan: record(camera))

    while True:
            sleep(0.1)


GPIO.cleanup()
