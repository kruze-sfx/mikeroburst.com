#!/usr/bin/env python
from __future__ import print_function

import argparse
import os
import shlex
import subprocess

import convert_icon_files

CONVERT_CMD = ('convert -limit memory 2048gb -resize "x{height}" '
               '-sharpen 1x1 -compress JPEG -quality 45 '
               '"{source}" "{dest}"')
ICON_FILE = '_icon.jpg'
SIZES = (20, 100, 250, 500,)
THUMB_DIR = '_thumbnail'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='image file to create icons for')
    parser.add_argument('--use-existing-icon', help='treat this as the icon '
                        'file for a directory', action='store_true')
    parser.add_argument('--overwrite', help='overwrite existing thumbnails',
                        action='store_true')
    return parser.parse_args()


def make_thumbnail(source, dest, height):
    cmd = CONVERT_CMD.format(height=height, source=source, dest=dest)
    print(cmd)
    subprocess.check_call(shlex.split(cmd))


def get_thumb_path(filename, height):
    dirname = os.path.dirname(filename)
    thumb_path = os.path.join(dirname, THUMB_DIR, str(height))
    if not os.path.isdir(thumb_path):
        print("mkdir {}".format(thumb_path))
        os.mkdir(thumb_path)
    return thumb_path


def is_valid_image(name_only):
    if name_only == ICON_FILE:
        return False
    elif not name_only.endswith('jpg'):
        return False
    else:
        return True


def use_existing_icon(filename, overwrite=False):
    original = convert_icon_files.find_original(filename)
    if original and os.path.exists(original):
        for height in SIZES:
            thumb_path = get_thumb_path(original, height)
            dest = os.path.join(thumb_path, ICON_FILE)
            if overwrite or not os.path.exists(dest):
                make_thumbnail(original, dest, height)
    else:
        raise ValueError("No original image found for {}".format(filename))


def process_image(filename, overwrite=False):
    name_only = os.path.basename(filename)
    if not is_valid_image(name_only):
        return
    for height in SIZES:
        thumb_path = get_thumb_path(filename, height)
        dest = os.path.join(thumb_path, name_only)
        if overwrite or not os.path.exists(dest):
            make_thumbnail(filename, dest, height)


def main():
    args = parse_args()

    if not os.path.exists(args.filename):
        raise OSError("No such file {}".format(args.filename))

    if args.use_existing_icon:
        use_existing_icon(args.filename, overwrite=args.overwrite)
    else:
        process_image(args.filename, overwrite=args.overwrite)


if __name__ == '__main__':
    main()