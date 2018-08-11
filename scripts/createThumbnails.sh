#!/bin/sh
HEIGHT=$1

DEFAULT_HEIGHT=150

numbers='^[0-9]+$'
if ! [[ $HEIGHT =~ $numbers ]] ; then
   echo "warning: HEIGHT not a number: ${HEIGHT}, falling back to ${DEFAULT_HEIGHT}" >&2
   HEIGHT=$DEFAULT_HEIGHT
else
   shift
fi

mkdir _thumbnail
for filename in "$@"; do
    if [ -f $filename ]; then
        convert -limit memory 2048gb -resize "x${HEIGHT}" -unsharp 1x1 -gravity SouthEast -compress JPEG -quality 45 $filename _thumbnail/thumb_$filename
    fi
    #echo "Created thumbnail for $filename"
done

