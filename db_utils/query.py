import os
import pprint
import sys

import MySQLdb

import db_utils.record_types as record_types

DIR_TYPE = 'dir'
DIRS_TABLE = 'dirs'
IMAGE_TYPE = 'image'
PHOTOS_TABLE = 'photos'


QUERY_PHOTO_STATEMENT = """SELECT * FROM {} WHERE user_path = %s {{}}
    """.format(PHOTOS_TABLE)

QUERY_DIR_STATEMENT = """SELECT * FROM {} WHERE parent_user_path = %s {{}}
    """.format(DIRS_TABLE)


class Querier(object):
    def __init__(self, host, user, password, db_name):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.db = None
        self.conn = None

    def connect(self):
        """
        Connect to the database
        """
        self.conn = MySQLdb.connect(host=self.host, user=self.user,
                                    passwd=self.password, db=self.db_name)
        self.db = self.conn.cursor()

    def close(self):
        """
        Close the connection to the database
        """
        if self.conn:
            self.conn.commit()
            self.db.close()
            self.conn.close()

    def get_path_contents(self, user_path):
        """
        Gets all the photos and subdirectories at a given path. The path is
        the path as seen by the user, as opposed to the path on disk.

        Optimized to return data so that the browser needs to do as little
        work as possible.

        :param user_path: The user path to query
        :return: dictionary of the format
            {
                'lightbox': [
                    # Content for the lightbox used to display single photos
                    # and move forward/backward between photos
                ],
                'grid': [
                    # Content to display the thumbnail grid at a given path
                ]
            }
        """
        photo_sort = self.get_photo_sort(user_path)
        photo_statement = QUERY_PHOTO_STATEMENT.format(photo_sort)
        self.db.execute(photo_statement, (user_path,))
        photos = [record_types.Photo(*p) for p in self.db.fetchall()]

        dir_sort = self.get_dir_sort(user_path)
        dir_statement = QUERY_DIR_STATEMENT.format(dir_sort)
        self.db.execute(dir_statement, (user_path,))
        dirs = [record_types.Dir(*d) for d in self.db.fetchall()]

        lightbox_info = self.get_lightbox_info(photos)
        grid_info = self.get_grid_info(photos, dirs)

        return {
            'user_path': user_path,
            'lightbox': lightbox_info,
            'grid': grid_info,
        }

    @staticmethod
    def get_lightbox_info(photos):
        """
        Builds a JSON list of photo info, to be passed to a lightbox app
        such as photoswipe
        """
        lightbox_info = []
        for photo in photos:
            if photo.created_time is not None:
                date_str = photo.created_time.strftime('%b %m %Y %H:%M:%S')
            else:
                date_str = "No date available"
            info = {
                'src': photo.url,  # required for photoswipe
                'w': photo.width,  # required for photoswipe
                'h': photo.height,  # required for photoswipe
                'pid': photo.filename,  # used for direct URL to image
                'title': photo.filename,  # photoswipe key for caption
                'created_time': date_str,
                'size': photo.size,
                'filename': photo.filename,  # for caption purposes only
                'exif_fstop': photo.exif_fstop,
                'exif_focal_length': photo.exif_focal_length,
                'exif_iso': photo.exif_iso,
                'exif_shutter_speed': photo.exif_shutter_speed,
                'exif_camera': photo.exif_camera,
                'exif_lens': photo.exif_lens,
                'exif_gps_lat': photo.exif_gps_lat,
                'exif_gps_lon': photo.exif_gps_lon,
                'exif_gps_alt_ft': photo.exif_gps_alt_ft,
            }
            lightbox_info.append(info)
        return lightbox_info

    @staticmethod
    def get_grid_info(photos, dirs):
        """
        Builds a JSON object containing information about photos and
        directories at a path, so they can be rendered into a grid view.
        """
        info = []

        # Show directories first
        for dir_ in dirs:
            dir_info = {
                'imageSizes': {
                    20: dir_.thumb_20_url,
                    100: dir_.thumb_100_url,
                    250: dir_.thumb_250_url,
                    500: dir_.thumb_500_url,
                },
                'aspectRatio': dir_.aspect_ratio,
                'metadata': {
                    'name': dir_.name,
                    'url': dir_.url,
                    'type': DIR_TYPE,
                    'num_photos': dir_.num_photos,
                    'num_subdirs': dir_.num_subdirs,
                }
            }
            info.append(dir_info)

        # Show photos after directories
        for photo_index, photo in enumerate(photos):
            photo_info = {
                'imageSizes': {
                    20: photo.thumb_20_url,
                    100: photo.thumb_100_url,
                    250: photo.thumb_250_url,
                    500: photo.thumb_500_url,
                },
                'aspectRatio': photo.aspect_ratio,
                'metadata': {
                    'name': photo.filename,
                    'type': IMAGE_TYPE,
                    'lightboxIndex': photo_index,
                }
            }
            info.append(photo_info)

        return info

    def get_photo_sort(self, user_path):
        """
        Gets a string that can be passed to an ORDER BY clause in SQL to
        control the sort order for photos for a given path.
        """
        # Always sort by filename
        return "ORDER BY filename ASC"

    def get_dir_sort(self, user_path):
        """
        Gets a string that can be passed to an ORDER BY clause in SQL to
        control the sort order for directories for a given path.
        """
        if user_path == "/":
            return "ORDER BY name ASC"
        else:
            return "ORDER BY name DESC"


def main():
    """
    For testing
    """
    # Let these generate KeyErrors if the env vars don't exist
    host = os.environ['PHOTOS_DB_HOST']
    user = os.environ['PHOTOS_DB_USER']
    password = os.environ['PHOTOS_DB_PASSWORD']
    db = os.environ['PHOTOS_DB_NAME']

    q = Querier(host, user, password, db)
    q.connect()
    pprint.pprint(q.get_path_contents(sys.argv[1]))


if __name__ == '__main__':
    main()

