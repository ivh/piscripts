import os
import subprocess
import errno
import numpy as np
from time import sleep
import arrow
from datetime import datetime,timedelta
notifyDelta = timedelta(minutes=15)
lastNotify = datetime.now() - notifyDelta

SAVEDIR='/home/pi/cams/'

from pushover import Pushover
po = Pushover(os.environ.get('NOTIFY_APPKEY'))
po.user(os.environ.get('NOTIFY_USERKEY'))

def notify(po , title='Hej!', message='Foo', url=None):
    global lastNotify
    if (datetime.now() - lastNotify) < notifyDelta:
        return
    msg=po.msg(message)
    msg.set('title',title)
    if url:
        msg.set('url',url)
    po.send(msg)
    lastNotify = datetime.now()

def make_sure_dir_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def getFileName(prefix='',suffix='jpg',base=SAVEDIR):
    timestring = arrow.utcnow().to('Europe/Stockholm').format(\
                        'YYYY-MM-DD_HH-mm-ss')
    make_sure_dir_exists(base)
    return  os.path.join(base, '.'.join((prefix, timestring, suffix)))


def rebin_factor( a, newshape ):
        '''Rebin an array to a new shape.
        newshape must be a factor of a.shape.
        '''
        assert len(a.shape) == len(newshape)
        assert not np.sometrue(np.mod( a.shape, newshape ))

        slices = [ slice(None,None, old/new) for old,new in zip(a.shape,newshape) ]
        return a[slices]

