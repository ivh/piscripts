#!/usr/bin/env python

import picamera
import picamera.array
from camcommon import *

#capture_size = (1296,972)
#capture_size = (640,480)
capture_size = (864,648)
motion_size = (640,480)
thresh = 20
sensit = 200

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
            camera.capture(fname,use_video_port=True, quality = 70)
            notify('PiCam: ' + fname.split('/')[-1], updateGallery=True)

with picamera.PiCamera() as camera:
    with DetectMotion(camera, size=motion_size) as output:
        camera.resolution = capture_size
        camera.framerate = 2
        camera.rotation = 180
        camera.start_preview()
        sleep(4)
        camera.start_recording('/dev/null',
            format='h264', motion_output=output, resize=motion_size)

        try:
            while True:
                camera.wait_recording(1)
        finally:
            camera.stop_recording()
