#!/usr/bin/env python
import os
import numpy as np
from PIL import Image
from StringIO import StringIO
import requests
from time import sleep
from datetime import datetime,timedelta
import scipy.ndimage as ndimage

CAMUSR = os.environ['CAMUSR']
CAMPWD= os.environ['CAMPWD']
USRPWD = (CAMUSR,CAMPWD)
#VIDURL = 'http://192.168.1.6/video.cgi'
PICURL = 'http://192.168.1.6/image.jpg'
SAVEDIR = '/home/pi/webcam/'

DET_INTERVAL = 2
RECORD_DURATION = 10
THRESH = 65
MINPIX = 1800

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



def getImage():
    req=requests.get(PICURL,auth=requests.auth.HTTPBasicAuth(*USRPWD))
    return Image.open(StringIO(req.content))

def rebin_factor( a, newshape ):
        '''Rebin an array to a new shape.
        newshape must be a factor of a.shape.
        '''
        assert len(a.shape) == len(newshape)
        assert not np.sometrue(np.mod( a.shape, newshape ))

        slices = [ slice(None,None, old/new) for old,new in zip(a.shape,newshape) ]
        return a[slices]

def img2sum(img):
    chansum = np.sum(np.asarray(img,dtype='Int32'),axis=-1)
    binned = rebin_factor(chansum,(240,320))
    return ndimage.gaussian_filter(binned,1.5)

def detectMotion(curr,last):
    curr = img2sum(curr)
    last = img2sum(last)
    diff = np.abs(curr-last)
    mask = diff > THRESH
    n = np.sum(mask)
    isMoving = n > MINPIX
    if isMoving:
        #Image.fromarray(mask.astype(np.uint8)*254).save(getFileName('mask-','.png'))
        print 'Motion %s:'%n + datetime.now().isoformat()
    return isMoving

def getFileName(prefix='motionIMG-',suffix='.jpg',dir=SAVEDIR):
    timestring = datetime.now().isoformat().split('.')[0]
    timestring = timestring.replace(':','-')
    return dir + prefix + timestring + suffix

def main():

    last=getImage()
    while True:
        curr = getImage()
        if detectMotion(curr,last):
            curr.transpose(Image.ROTATE_270).save(getFileName(),format='jpeg')
            notify('Webcam motion')

        last=curr
        sleep(DET_INTERVAL)



if __name__ == '__main__':
    main()
