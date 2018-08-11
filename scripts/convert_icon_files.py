#!/usr/bin/env python
"""
A script to convert from legacy _icon files to multiple size-based
thumbnails.

Does this by looking at the EXIF data of the _icon.jpg file and trying to
guess which original image it came from, based on creation date. If no
original image could be determined, prints that filename for manual
intervention.
"""
from __future__ import print_function

import argparse
import os
import sys

import exifread


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('icon_file', help='Filename of the legacy _icon.jpg '
                        'file to be converted')
    return parser.parse_args()


def _exif_val(tags, key, default=None, index=None):
    try:
        if index is None:
            return tags[key].values
        else:
            return tags[key].values[index]
    except KeyError:
        return default


def get_created_date(filename):
    with open(filename, 'rb') as f:
        tags = exifread.process_file(f)
    return _exif_val(tags, 'EXIF DateTimeOriginal', '')


def does_match(candidate, icon_created):
    candidate_created = get_created_date(candidate)
    #if candidate_created == icon_created:
    #    print("original {} == candidate {}".format(icon_created, candidate_created))
    #else:
    #    print("original {} != candidate {}".format(icon_created, candidate_created))

    return candidate_created == icon_created


def find_original(icon_file):
    # Get the created date of the original icon file
    icon_created = get_created_date(icon_file)

    # Scan the other files in the same directory and find one with the exact
    # same created date
    dir_name = os.path.dirname(icon_file) or '.'
    walk_iter = os.walk(dir_name)
    _, _, files = next(walk_iter)
    for f in files:
        candidate = os.path.join(dir_name, f)
        if candidate == icon_file:
            continue
        #print("Checking {}".format(candidate))
        if does_match(candidate, icon_created):
            return candidate
    # If we got this far, there's no match
    return None


def main():
    args = parse_args()

    match = find_original(args.icon_file)
    if match is None:
        print("{}: no match found".format(args.icon_file))
        sys.exit(-1)
    else:
        print(match)
        sys.exit(0)


if __name__ == '__main__':
    main()
