SAVEDIR='/home/pi/cams/'

import os
import subprocess
import errno
import numpy as np
from time import sleep

from datetime import datetime,timedelta
datestring = str(datetime.today().date())

import pushnotify as pn
pn.logging.basicConfig()
NOTIFY_APPKEY = os.environ.get('NOTIFY_APPKEY')
NOTIFY_USERKEY = os.environ.get('NOTIFY_USERKEY')
p=pn.pushover.Client(developerkey=NOTIFY_APPKEY)
p.apikeys={NOTIFY_USERKEY:[]}
notifyDelta = timedelta(minutes=15)
lastNotify = datetime.now() - notifyDelta

def notify(descr, title='Motion',
        url='https://oin.tmy.se/%s/'%datestring, urltitle='Go to gallery...',
        updateGallery=False):

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

    if updateGallery:
        updateGallery()

def updateGallery(src='/home/pi/cams/', dst='/home/pi/www/',
                    cfg='/home/pi/.sigal.conf'):
    devnull = open(os.devnull, 'wb')
    cmd = 'sleep 10 && sigal build -c %s %s %s'%(cfg, src, dst)
    subprocess.Popen(cmd, shell=True, stdout=devnull, stderr=devnull)


def make_sure_dir_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def getFileName(prefix='',suffix='.jpg',base=SAVEDIR):
    timestring = datetime.now().isoformat()
    timestring = timestring.replace(':','-')
    datestring = timestring.split('T')[0]
    make_sure_dir_exists(os.path.join(base, datestring))
    return  os.path.join(base, datestring, prefix + timestring + suffix)


def rebin_factor( a, newshape ):
        '''Rebin an array to a new shape.
        newshape must be a factor of a.shape.
        '''
        assert len(a.shape) == len(newshape)
        assert not np.sometrue(np.mod( a.shape, newshape ))

        slices = [ slice(None,None, old/new) for old,new in zip(a.shape,newshape) ]
        return a[slices]
