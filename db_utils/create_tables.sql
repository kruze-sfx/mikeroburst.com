DROP TABLE IF EXISTS photos;
DROP TABLE IF EXISTS dirs;

CREATE TABLE photos (
    user_path VARCHAR(254),
    filename VARCHAR(254),
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
    exif_fstop VARCHAR(12),
    exif_focal_length VARCHAR(12),
    exif_iso VARCHAR(12),
    exif_shutter_speed VARCHAR(12),
    exif_camera VARCHAR(64),
    exif_lens VARCHAR(64),
    exif_gps_lat VARCHAR(64),
    exif_gps_lon VARCHAR(64),
    exif_gps_alt_ft VARCHAR(8),
    PRIMARY KEY (user_path, filename)
);
CREATE INDEX photos_by_user_path ON photos(`user_path`);

CREATE TABLE dirs (
    user_path VARCHAR(254),
    parent_user_path VARCHAR(254),
    name VARCHAR(254),
    url VARCHAR(254),
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
    PRIMARY KEY (user_path)
);
CREATE INDEX dirs_by_user_path ON dirs(`user_path`);
