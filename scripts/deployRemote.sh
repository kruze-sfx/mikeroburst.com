#!/bin/bash
BASEPATH="/Volumes/DroboPrimary/Pictures/webpics/albums"

echo "Rsync\'ing pictures..."

rsync  --delete -avz -e "ssh -l kruzem" $BASEPATH www.mikeroburst.com:mikeroburst.com/pics/

