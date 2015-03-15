#!/usr/bin/env python
import os
import numpy as np
import picamera
import picamera.array
from time import sleep
from datetime import datetime,timedelta

#capture_size = (1296,972)
#capture_size = (640,480)
capture_size = (864,648)
motion_size = (640,480)
thresh = 20
sensit = 200

SAVEDIR='/home/pi/piCam/'

import pushnotify as pn
pn.logging.basicConfig()
NOTIFY_APPKEY = os.environ['NOTIFY_APPKEY']
NOTIFY_USERKEY = os.environ['NOTIFY_USERKEY']
p=pn.pushover.Client(developerkey=NOTIFY_APPKEY)
p.apikeys={NOTIFY_USERKEY:[]}
notifyDelta = timedelta(minutes=15)
lastNotify = datetime.now() - notifyDelta

def notify(descr,title=None,url=None,urltitle=None):
    global lastNotify
    if (datetime.now() - lastNotify) < notifyDelta:
        return
    if not title:
        title=descr
    if not url:
        kwargs = None
    else:
        if not urltitle:
            urltitle=url
        kwargs={'url':url,'url_title':urltitle}
    p.notify(description=descr,event=title,kwargs=kwargs)
    lastNotify = datetime.now()

def getFileName(prefix='motionIMG-',suffix='.jpg',dir=SAVEDIR):
    timestring = datetime.now().isoformat()
    timestring = timestring.replace(':','-')
    return dir + prefix + timestring + suffix

class DetectMotion(picamera.array.PiMotionAnalysis):
    def analyse(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        asum = (a > thresh).sum()
        if asum > sensit:
            print 'Capturing a=%s: '%asum + datetime.now().isoformat()
            fname = getFileName()
            #camera.capture_sequence(
            #    [getFileName(suffix='')+'_%02d.jpg'%i for i in range(3)],
            camera.capture(fname,use_video_port=True, quality = 30)
            notify('PiCam motion!')

with picamera.PiCamera() as camera:
    with DetectMotion(camera, size=motion_size) as output:
        camera.resolution = capture_size
        camera.framerate = 2
        camera.rotation = 180
        camera.start_preview()
        sleep(5)
        camera.start_recording('/dev/null',
            format='h264', motion_output=output, resize=motion_size)

        try:
            while True:
                camera.wait_recording(1)
        finally:
            camera.stop_recording()
