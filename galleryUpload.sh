#!/bin/bash

src='/home/pi/cams/'
dst='/home/pi/www/'
cfg='/home/pi/.sigal.conf'
                                
sleep 25
sigal build -c $cfg $src $dst

rsync -aP --delete /home/pi/cams /home/pi/www bomba:sites/oin/ 
