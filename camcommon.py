import os
import subprocess
import errno
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

