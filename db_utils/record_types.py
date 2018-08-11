import collections

Photo = collections.namedtuple(
    'Photo', ['path', 'user_path', 'filename', 'url', 'thumb_20_url',
              'thumb_100_url', 'thumb_250_url', 'thumb_500_url',
              'created_time', 'width', 'height', 'aspect_ratio', 'size',
              'modified_time', 'exif_fstop', 'exif_focal_length', 'exif_iso',
              'exif_shutter_speed', 'exif_camera', 'exif_lens', 'exif_gps_lat',
              'exif_gps_lon', 'exif_gps_alt_ft'])

Dir = collections.namedtuple(
    'Dir', ['path', 'user_path', 'parent_user_path', 'name', 'url',
            'thumb_20_url', 'thumb_100_url', 'thumb_250_url', 'thumb_500_url',
            'width', 'height', 'aspect_ratio', 'created_time', 'modified_time',
            'num_subdirs', 'num_photos'])

Exif = collections.namedtuple(
    'Exif', ['width', 'height', 'created', 'fstop', 'focal_length', 'iso',
             'shutter_speed', 'camera', 'lens', 'gps_lat', 'gps_lon',
             'gps_alt_ft'])
