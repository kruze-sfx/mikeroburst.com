#!/bin/sh
set -ex

ORIG_DIR=$PWD

find . -maxdepth 1 -mindepth 1 -type d | while read dirname; do
    cd "$dirname"
    ~/git/scratch/preview.mikeroburst.com/scripts/createThumbnailsNew.sh *.jpg
    cd "$ORIG_DIR"
done
