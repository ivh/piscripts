#!/bin/bash
directories=( "/home/pi/cams" )
inotifywait -q --monitor --event close_write,moved_to --format '%w%f' "${directories[@]}" | while read thing ; do
    [ -f "$thing" ] || continue
		scp "$thing" ori:cams/  > /dev/null;
		echo "Uploaded $thing" ;
done

