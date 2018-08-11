#!/usr/bin/env python

import argparse
import datetime
import getpass
import mock
import os

import exifread
import MySQLdb

import db_utils.record_types as record_types

DIRS_TABLE = 'dirs'
ICON_FILE = '_icon.jpg'
MD5_CHUNK_SIZE = 2 ** 22  # 4 MB
PHOTOS_TABLE = 'photos'
SUPPORTED_TYPES = frozenset(('.jpg', '.png', '.tif'))
THUMBS_DIR = '_thumbnail'
THUMB_PREFIX = 'thumb_'
THUMB_SIZES = ('20', '100', '250', '500')
UNDEFINED_INT = -1
UNDEFINED_STR = 'Unavailable'
PHOTO_URL_ROOT = '/photo'
DIR_URL_ROOT = '/photos'
USER_ROOT = '/'
DEFAULT_THUMB_URL = '/static/default_thumbnails'
DEFAULT_THUMB_DISK_PATH = 'static/default_thumbnails'  # TODO: Make this not hard-coded

EXCLUDE_DIRS = frozenset((THUMBS_DIR,))

INDEX_PHOTO_STATEMENT = """INSERT INTO {}
    (path, user_path, filename, url, thumb_20_url, thumb_100_url,
     thumb_250_url, thumb_500_url, created_time, width, height, aspect_ratio,
     size, modified_time, exif_fstop, exif_focal_length, exif_iso,
     exif_shutter_speed, exif_camera, exif_lens, exif_gps_lat, exif_gps_lon,
     exif_gps_alt_ft)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s)
    """

INDEX_DIR_STATEMENT = """INSERT INTO {}
    (path, user_path, parent_user_path, name, url, thumb_20_url, thumb_100_url,
     thumb_250_url, thumb_500_url, width, height, aspect_ratio, created_time,
     modified_time, num_subdirs, num_photos)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='The directory path to index',
                        required=True)
    parser.add_argument('--root', help='The root of all photos. Will be '
                        'excluded from the path', required=True)
    parser.add_argument('--db-host', help='mysql host', required=True)
    parser.add_argument('--db-user', help='mysql user', required=True)
    parser.add_argument('--db-name', help='mysql database name', required=True)
    parser.add_argument('--force', action='store_true',
                        help="If specified, don't check for an "
                        'existing entry in the database, always index')
    parser.add_argument('--for-real', action='store_true',
                        help="Serious this time")
    return parser.parse_args()


def walk_path(db, path, root):
    for dirpath, dirnames, filenames in os.walk(path, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        index_dir(db, root, dirpath, dirnames, filenames)


def index_dir(db, root, dirpath, dirnames, filenames):
    """
    Reference of variable names used here for the example path
    "/photos/albums/2017/2017 08-19 Yosemite"

    dirpath = path = "/photos/albums/2017/2017 08-19 Yosemite"
    root = "/photos/albums"
    user_path = "2017/2017 08-19 Yosemite"
    name = "2017 08-19 Yosemite"
    """
    # Index all non-thumbnail photos
    for filename in filenames:
        index_photo(db, root, dirpath, filename)

    # Index the directory itself
    num_subdirs = len([d for d in dirnames if not d.endswith(THUMBS_DIR)])
    user_path = dirpath.lstrip(root)
    thumb_urls = get_dir_thumb_urls(dirpath, user_path)
    width, height, aspect_ratio = get_dir_thumbnail_dimensions(dirpath)
    # num_photos is not a recursive sum (though maybe it should be)
    num_photos = len([f for f in filenames if f != ICON_FILE])
    dir_obj = record_types.Dir(
        path=dirpath,
        user_path=user_path,
        parent_user_path=get_parent_dir(user_path),
        name=os.path.basename(dirpath),
        url=get_dir_url(user_path),
        thumb_20_url=thumb_urls[0],
        thumb_100_url=thumb_urls[1],
        thumb_250_url=thumb_urls[2],
        thumb_500_url=thumb_urls[3],
        width=width,
        height=height,
        aspect_ratio=aspect_ratio,
        created_time=_convert_epoch_timestamp(os.path.getctime(dirpath)),
        modified_time=_convert_epoch_timestamp(os.path.getmtime(dirpath)),
        num_subdirs=num_subdirs,
        num_photos=num_photos,
    )
    db.execute(INDEX_DIR_STATEMENT.format(DIRS_TABLE), dir_obj)


def index_photo(db, root, dirpath, filename):
    # Don't index icons
    if filename == ICON_FILE:
        return
    # Don't index unsupported types
    if not is_image_supported(filename):
        return

    # The "path" includes the root and points to the actual file on disk.
    # The "user_path" is what appears to the user and the breadcrumb hierarchy.
    path = os.path.join(dirpath, filename)
    user_path = dirpath.lstrip(root)

    exif = get_exif(path)
    thumb_urls = get_photo_thumb_urls(dirpath, user_path, filename)

    # Format the modified time as a sql datetime
    modified_dt = _convert_epoch_timestamp(os.path.getmtime(path))

    photo = record_types.Photo(
        path=path,
        user_path=user_path,
        filename=filename,
        url=get_image_url(user_path, filename),
        thumb_20_url=thumb_urls[0],
        thumb_100_url=thumb_urls[1],
        thumb_250_url=thumb_urls[2],
        thumb_500_url=thumb_urls[3],
        created_time=exif.created,
        width=exif.width,
        height=exif.height,
        aspect_ratio=(exif.width / exif.height),
        size=os.path.getsize(path),
        modified_time=modified_dt,
        exif_fstop=exif.fstop,
        exif_focal_length=exif.focal_length,
        exif_iso=exif.iso,
        exif_shutter_speed=exif.shutter_speed,
        exif_camera=exif.camera,
        exif_lens=exif.lens,
        exif_gps_lat=exif.gps_lat,
        exif_gps_lon=exif.gps_lon,
        exif_gps_alt_ft=exif.gps_alt_ft,
    )
    db.execute(INDEX_PHOTO_STATEMENT.format(PHOTOS_TABLE), photo)


def is_image_supported(filename):
    extension = os.path.splitext(filename)[1].lower()
    return extension in SUPPORTED_TYPES


def get_image_url(user_path, filename):
    """
    Gets the URL for a full-sized image
    """
    return os.path.join(PHOTO_URL_ROOT, user_path.lstrip('/'), filename)


def get_dir_url(user_path):
    """
    Gets the URL for a directory
    """
    return os.path.join(DIR_URL_ROOT, user_path.lstrip('/'))


def get_photo_thumb_urls(dirpath, user_path, filename):
    res = []
    for size in THUMB_SIZES:
        res.append(get_thumb_url(dirpath, user_path, filename, size))
    return res


def get_dir_thumb_urls(dirpath, user_path):
    res = []
    for size in THUMB_SIZES:
        res.append(get_thumb_url(dirpath, user_path, ICON_FILE, size))
    return res


def get_thumb_url(dirpath, user_path, filename, size):
    """
    Gets a URL for the thumbnail of a given photo filename and size
    """
    on_disk_thumb_file = os.path.join(dirpath, THUMBS_DIR, size, filename)
    if os.path.exists(on_disk_thumb_file):
        url = os.path.join(PHOTO_URL_ROOT, user_path.lstrip('/'), THUMBS_DIR,
                           size, filename)
    else:
        url = os.path.join(DEFAULT_THUMB_URL, size, filename)
    return url


def get_dir_thumb_file(dirpath, size):
    """
    Gets the path to a filename for a directory icon. Returns the actual
    on-disk path that can be accessed by python.
    """
    thumb_file = os.path.join(dirpath, THUMBS_DIR, size, ICON_FILE)
    if os.path.exists(thumb_file):
        return thumb_file
    else:
        return os.path.join(DEFAULT_THUMB_DISK_PATH, size, ICON_FILE)


def get_dir_thumbnail_dimensions(dirpath):
    """
    In order to show a directory thumbnail image in the image grid properly,
    we need to know the dimensions and aspect ratio of the thumbnail.
    """
    # Use the largest thumbnail size to calculate the aspect ratio.
    size = THUMB_SIZES[-1]
    thumb_file = get_dir_thumb_file(dirpath, size)
    exif = get_exif(thumb_file)
    return exif.width, exif.height, (exif.width / exif.height)


def get_parent_dir(user_path):
    if user_path == USER_ROOT:
        return None
    else:
        return os.path.dirname(user_path)


def _exif_val(tags, key, default=None, index=None):
    try:
        if index is None:
            return tags[key].values
        else:
            return tags[key].values[index]
    except KeyError:
        return default


def get_exif(path):
    """Returns an Exif namedtuple of exif data in an image"""
    with open(path, 'rb') as f:
        tags = exifread.process_file(f)
    width = _exif_val(tags, 'EXIF ExifImageWidth', UNDEFINED_INT, 0)
    height = _exif_val(tags, 'EXIF ExifImageLength', UNDEFINED_STR, 0)
    created = _exif_val(tags, 'EXIF DateTimeOriginal', UNDEFINED_STR)
    camera_make = _exif_val(tags, 'Image Make', UNDEFINED_STR)
    camera_model = _exif_val(tags, 'Image Model', UNDEFINED_STR)
    lens = _exif_val(tags, 'EXIF LensModel', UNDEFINED_STR)
    speed = str(_exif_val(tags, 'EXIF ExposureTime', UNDEFINED_STR, 0))
    focal_length = _exif_val(tags, 'EXIF FocalLength', UNDEFINED_STR, 0)
    fstop = _exif_val(tags, 'EXIF FNumber', UNDEFINED_STR, 0)  # Ratio object
    iso = str(_exif_val(tags, 'EXIF ISOSpeedRatings', UNDEFINED_STR, 0))
    # TODO: GPS

    # Format fstop and camera
    if fstop != UNDEFINED_STR:
        fstop_formatted = '{:.1f}'.format(fstop.num / fstop.den)
    else:
        fstop_formatted = UNDEFINED_STR
    if camera_make != UNDEFINED_STR and camera_model != UNDEFINED_STR:
        camera_formatted = '{} {}'.format(camera_make, camera_model)
    else:
        camera_formatted = UNDEFINED_STR

    # Format datetime fields
    created_dt = _convert_exif_timestamp(created)

    # Format focal length
    if focal_length != UNDEFINED_STR:
        focal_length_fmt = '{:d}'.format(focal_length.num // focal_length.den)
    else:
        focal_length_fmt = UNDEFINED_STR

    return record_types.Exif(
        width=width, height=height, created=created_dt, fstop=fstop_formatted,
        focal_length=focal_length_fmt, iso=iso, shutter_speed=speed,
        camera=camera_formatted, lens=lens, gps_lat=None, gps_lon=None,
        gps_alt_ft=None
    )


def _convert_exif_timestamp(exif_time):
    """Converts timestamp format in exif to a sql datetime

    For example:
    >>> _convert_exif_timestamp('2018:01:01 12:17:12')
    '2018-01-01 12:17:12'
    """
    if exif_time != UNDEFINED_STR:
        dt = datetime.datetime.strptime(exif_time, '%Y:%m:%d %H:%M:%S')
    else:
        dt = datetime.datetime.now()  # TODO: Is that what we want?
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def _convert_epoch_timestamp(epoch_time):
    """Converts an epoch timestamp (in seconds) to a sql datetime

    For example:
    >>> _convert_epoch_timestamp(1514963798.0)
    '2018-01-02 23:16:38'
    """
    return datetime.datetime.fromtimestamp(epoch_time).strftime(
        '%Y-%m-%d %H:%M:%S')


def mock_execute(query, obj):
    print(query % obj)


def main():
    args = parse_args()
    if args.for_real:
        passwd = getpass.getpass(
            'mysql password for user {}: '.format(args.db_user))
        conn = MySQLdb.connect(host=args.db_host, user=args.db_user,
                               passwd=passwd, db=args.db_name)
        db = conn.cursor()
    else:
        db = mock.Mock()
        conn = mock.Mock()
        db.execute = mock_execute
    try:
        walk_path(db, args.path, args.root)
    finally:
        conn.commit()
        db.close()
        conn.close()


if __name__ == '__main__':
    main()
