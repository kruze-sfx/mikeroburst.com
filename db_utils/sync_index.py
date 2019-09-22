import argparse
import getpass
import pprint
import os
import os.path

import MySQLdb

import db_utils.indexer as indexer


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


def walk_local_dirs(path, root):
    path_files = {}
    for dirpath, dirnames, filenames in os.walk(path, topdown=True,
                                                followlinks=True):
        dirnames[:] = [d for d in dirnames if d not in indexer.EXCLUDE_DIRS]
        user_path = indexer.get_user_path(dirpath, root)

        filtered_files = set(
            f for f in filenames if f != indexer.ICON_FILE)
        path_files[user_path] = (dirpath, dirnames, filtered_files)
    return path_files


def sync(db, path, root, for_real):
    # Get a mapping of dir user path to tuple of
    # (dirpath, dirnames, filenames)
    path_info = walk_local_dirs(path, root)

    # Add any dirs (and all their photos) that exist locally but not
    # in the DB.
    # Delete any dirs (and all their photos) in the DB that don't
    # exist locally.
    sync_dirs(db, path, root, path_info, for_real)

    # At this point all of the dirs have been synced, all of the photos
    # in removed dirs have been removed from the DB, and all of the
    # photos in the added dirs have been added to the DB.
    # Now we want to handle changes in the photos whose dirs haven't
    # changed.
    for user_path, info in path_info.items():
        dirpath, dirnames, filenames = info
        sync_photos(db, dirpath, user_path, filenames, for_real)


def sync_dirs(db, path, root, path_info, for_real):
    local_user_paths = set(path_info.keys())

    # Get the set of dir user paths in the DB matching the user path of
    # the passed-in local path.
    dir_user_path = indexer.get_user_path(path, root)
    paths_in_db = set(indexer.get_dirs_for_sync(db, dir_user_path))

    dirs_to_add = local_user_paths - paths_in_db
    dirs_to_remove = paths_in_db - local_user_paths

    for user_path in dirs_to_add:
        info = path_info[user_path]
        dirpath, dirnames, filenames = info
        indexer.index_dir(db, root, dirpath, dirnames, filenames, for_real)

    for user_path in dirs_to_remove:
        indexer.delete_dir(db, user_path, for_real)
        indexer.delete_photos_in_dir(db, user_path, for_real)


def sync_photos(db, dirpath, user_path, filenames, for_real):
    photos_to_add = set()
    photos_to_remove = set()
    photos_in_db = indexer.get_photos_for_sync(db, user_path)
    # Add files that are local but not in the DB.
    # Also add files that are in the DB but the local one has
    # a different timestamp.
    for local_file in filenames:
        if local_file not in photos_in_db:
            photos_to_add.add(local_file)
        else:
            db_mtime = photos_in_db[local_file]
            local_mtime = os.path.getmtime(os.path.join(dirpath, local_file))
            if db_mtime != local_mtime:
                photos_to_add.add(local_file)
    # Remove files that are in the DB but not local
    for db_file in photos_in_db:
        if db_file not in filenames:
            photos_to_remove.add(db_file)
    # Assert that we're not removing and adding the same photos
    assert not photos_to_remove & photos_to_add

    for filename in photos_to_add:
        indexer.index_photo(db, user_path, dirpath, filename, for_real)
    for filename in photos_to_remove:
        indexer.delete_photo(db, user_path, filename, for_real)
    # TODO: Need to update num_subdirs and num_photos for the dir


def main():
    args = parse_args()
    passwd = getpass.getpass(
        'mysql password for user {}: '.format(args.db_user))
    conn = MySQLdb.connect(host=args.db_host, user=args.db_user,
                           passwd=passwd, db=args.db_name)
    db = conn.cursor()
    path = os.path.abspath(args.path)
    root = os.path.abspath(args.root)
    try:
        sync(db, path, root, args.for_real)
    finally:
        conn.commit()
        db.close()
        conn.close()


if __name__ == '__main__':
    main()
