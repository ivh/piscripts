#!/usr/bin/env python
from PIL import Image
from StringIO import StringIO
import requests
import scipy.ndimage as ndimage
from collections import deque

from camcommon import *

CAMUSR = os.environ['CAMUSR']
CAMPWD= os.environ['CAMPWD']
USRPWD = (CAMUSR,CAMPWD)
#VIDURL = 'http://192.168.1.6/video.cgi'
PICURL = 'http://192.168.1.6/image.jpg'

DET_INTERVAL = 2
RECORD_DURATION = 10
THRESH = 75
MINPIX = 2200


def getImage():
    req=requests.get(PICURL,auth=requests.auth.HTTPBasicAuth(*USRPWD))
    return Image.open(StringIO(req.content))

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

def main():
    lastOnes = deque((0,)*10,maxlen=10)
    last=getImage()
    while True:
        curr = getImage()
        if detectMotion(curr,last):
            fname = getFileName()
            curr.transpose(Image.ROTATE_270).save(fname,format='jpeg')
            notify('WebCam: ' + fname.split('/')[-1], updateGallery=True,
                    url=galleryurl(), urltitle='Go to gallery...')
            lastOnes.appendleft(1)
            print sum(lastOnes)
        last=curr
        sleep(DET_INTERVAL * (sum(lastOnes) + 1))



if __name__ == '__main__':
    main()
