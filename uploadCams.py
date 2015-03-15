#!/usr/bin/env python

import socket
import sys, os
import time

def get_lock(process_name='GUploader'):
    global lock_socket
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        lock_socket.bind('\0' + process_name)
    except socket.error:
        sys.exit()

get_lock()

photdirs = ['/home/pi/piCam']#, '/home/pi/webcam']
picam_albums = ['/data/feed/api/user/default/albumid/6126094662983072497',
                '/data/feed/api/user/default/albumid/6126351201939236849']

for i,photdir in enumerate(photdirs):
    os.chdir(photdir)
    timestamp = os.stat('timestamp').st_atime

    toupload = [ fname for fname in os.listdir(os.curdir)\
                 if os.stat(fname).st_atime > timestamp ]

    if toupload and 'gd_client' not in locals():
        import gdata.photos.service
        gd_client = gdata.photos.service.PhotosService()
        gd_client.email = os.environ['GMAIL']
        gd_client.source = 'ownPhotoUpload'
        gd_client.password= os.environ['GPWD']
        gd_client.ProgrammaticLogin()

    for fname in toupload:
        gd_client.InsertPhotoSimple(picam_albums[i], fname,
            'piCam.py upload', fname, content_type='image/jpeg')
        print fname

    os.utime('timestamp',None)

#phototitles = [photo.title.text for photo in
#                gd_client.GetFeed(picam_album).entry]
