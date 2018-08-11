DROP TABLE IF EXISTS photos;
DROP TABLE IF EXISTS dirs;

CREATE TABLE photos (
    path VARCHAR(256),
    user_path VARCHAR(256),
    filename VARCHAR(256),
    url VARCHAR(512),
    thumb_20_url VARCHAR(512),
    thumb_100_url VARCHAR(512),
    thumb_250_url VARCHAR(512),
    thumb_500_url VARCHAR(512),
    created_time DATETIME,
    width INT,
    height INT,
    aspect_ratio FLOAT,
    size BIGINT,
    modified_time DATETIME,
    exif_fstop VARCHAR(8),
    exif_focal_length VARCHAR(8),
    exif_iso VARCHAR(8),
    exif_shutter_speed VARCHAR(8),
    exif_camera VARCHAR(64),
    exif_lens VARCHAR(64),
    exif_gps_lat VARCHAR(64),
    exif_gps_lon VARCHAR(64),
    exif_gps_alt_ft VARCHAR(8),
    PRIMARY KEY (path, filename)
);
CREATE INDEX photos_by_user_path ON photos(`user_path`);

CREATE TABLE dirs (
    path VARCHAR(256),
    user_path VARCHAR(256),
    parent_user_path VARCHAR(256),
    name VARCHAR(256),
    url VARCHAR(256),
    thumb_20_url VARCHAR(512),
    thumb_100_url VARCHAR(512),
    thumb_250_url VARCHAR(512),
    thumb_500_url VARCHAR(512),
    width INT,
    height INT,
    aspect_ratio FLOAT,
    created_time DATETIME,
    modified_time DATETIME,
    num_subdirs INT,
    num_photos INT,
    PRIMARY KEY (path)
);
CREATE INDEX dirs_by_user_path ON dirs(`user_path`);
