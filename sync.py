#!/usr/bin/env python3
import sys
import os
import json
import time
import hashlib
import shutil

__author__ = 'Ofek'


def main(dir1, dir2):

    if not os.path.exists(dir1):  # ie folder exists
    # create folder
        os.makedirs(dir1)
    if not os.path.exists(dir2):  # ie folder exists
        # create folder
        os.makedirs(dir2)

    crawl_folders(dir1, dir2)
    sync1 = load_sync_json(dir1)
    sync2 = load_sync_json(dir2)
    update_sync(dir1, sync1)
    update_sync(dir2, sync2)
    sync(sync1, sync2, dir1, dir2)
    update_sync(dir1, sync1)
    update_sync(dir2, sync2)
    write_sync_file(dir1, sync1)
    write_sync_file(dir2, sync2)


"""
@function
Recursively crawl through all folders calling main
"""


def crawl_folders(dir1, dir2):
    #get all sub directories and union them, then call snycMain to start sync on those
    dir_one = [d for d in os.listdir(dir1) if os.path.isdir(os.path.join(dir1, d))]
    dir_two = [d for d in os.listdir(dir2) if os.path.isdir(os.path.join(dir2, d))]
    folders_to_sync = list(set(dir_one) | set(dir_two))
    for f in folders_to_sync:
        main(dir1+"/"+f, dir2+"/"+f)
    # if os.path.exists(dir1):  # ie folder exists
    #     dir_filenames = os.listdir(dir1)
    #     dir2_filenames = os.listdir(other_dir)
    #     for filename_dir2 in dir2_filenames:
    #         if any(filename_dir2 in filename_dir1 for filename_dir1 in dir_filenames):
    #             dir_filenames.append(filename_dir2)
    #     dir_filenames[:] = [name for name in dir_filenames if name != ".sync"]
    #     for filename in dir_filenames:
    #         # check if folder and if it is recall main function
    #         dir_path1 = os.path.join(dir1, filename)
    #         dir_path2 = os.path.join(other_dir, filename)
    #         if os.path.isdir(dir_path1) or os.path.isdir(dir_path2):
    #             if not os.path.exists(dir_path1):
    #                 os.makedirs(dir_path1)
    #             if not os.path.exists(dir_path2):
    #                 os.makedirs(dir_path2)
    #             main(dir_path1, dir_path2)
    #             dir_filenames.remove(filename)
    #             dir_filenames[:] = [name for name in dir_filenames if name != filename]


"""
@function
Load in the two folders and all their files, check if folders exist, if they do not, create the folders
"""


def load_files(dir):
    if os.path.exists(dir):  # ie folder exists
        dir_filenames = os.listdir(dir)
        for filename in dir_filenames:
            dir_path = os.path.join(dir, filename)
            if os.path.isdir(dir_path):
                dir_filenames.remove(filename)
    else:
        # create folder
        os.makedirs(dir)
        return []
    return dir_filenames


"""
@function
Write sync file
"""


def write_sync_file(dir, sync):
    sync_file = open(os.path.join(dir, ".sync"), 'w')
    print(json.dumps(sync), file=sync_file)


"""
@function
Update sync files
"""


def get_modification_date(pathname):
    mod_date = str(time.strftime('%Y-%m-%d %H:%M:%S %z', time.localtime(os.path.getmtime(pathname))))
    return mod_date  # datetime.datetime.fromtimestamp(os.path.getmtime(pathname))


def get_SHA(pathname):
    file = open(pathname, 'rb')
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with file as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def update_sync(dir, sync):
    dir_filenames = load_files(dir)
    for filename in dir_filenames:
        pathname = os.path.join(dir, filename)
        if os.path.isdir(pathname):
                dir_filenames.remove(filename)
                continue
        if filename != ".sync":
            if filename in sync:
                file_array = sync.get(filename)
                SHA = get_SHA(pathname)
                modification_date = get_modification_date(pathname)
                if SHA != file_array[0][1] or modification_date > (file_array[0][0]):
                    file_array.insert(0, [modification_date, SHA])
            else:
                # else add to dictionary as new entry
                sync[filename] = [[get_modification_date(pathname), get_SHA(pathname)]]
                # check if deleted
        for key in sync.keys():
            keyfound = False
            for filename in dir_filenames:
                if filename == key:
                    keyfound = True
                    break
            if not keyfound and sync[key][0][1] != "deleted":
                file_array = sync.get(key)
                file_array.insert(0, [time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime()), "deleted"])
                break


"""
@function
Read in sync file and or create it
"""


def load_sync_json(dir):
    sync_dir = os.path.join(dir, ".sync")

    if os.path.isfile(sync_dir):
        with open(sync_dir) as json_file:
            sync_loaded = json.load(json_file)
            return sync_loaded
    else:
        temp_file = open(sync_dir, 'a')
        print({}, file=temp_file)  # write empty braces to avoid json parsing errors
        return {}


"""
@function
Sync directories and update sync files
"""


def sync(sync1, sync2, dir1, dir2):
    for filename in sync1.keys():
        file_array = sync1[filename]
        latest_file_update_sync1 = file_array[0]

        # file deleted (need to check modification date if on other sync)
        # file deleted in sync 1 and most recent
        if latest_file_update_sync1[1] == "deleted" or filename in sync2 and sync2[filename][0][1] == "deleted":
            if repr(latest_file_update_sync1[0]) > repr(sync2[filename][0][0]) and latest_file_update_sync1[
                1] == "deleted":
                pathname = os.path.join(dir2, filename)
                if os.path.exists(pathname):
                    os.remove(pathname)
                continue
            # file deleted in sync 2 and most recent
            elif repr(latest_file_update_sync1[0]) < repr(sync2[filename][0][0]) and sync2[filename][0][1] == "deleted":
                pathname = os.path.join(dir1, filename)
                if os.path.exists(pathname):
                    os.remove(pathname)
                continue
                # file deleted in sync 1 or 2 and not most recent
            elif latest_file_update_sync1[1] == "deleted" and repr(latest_file_update_sync1[0]) < repr(
                    sync2[filename][0][0]) or sync2[filename][0][1] == "deleted" and repr(
                latest_file_update_sync1[0]) > repr(sync2[filename][0][0]):
                copy_latest_file(dir1, dir2, filename, latest_file_update_sync1, sync2[filename][0])
                continue

        # file not in other sync
        if filename not in sync2:
            pathname = os.path.join(dir1, filename)
            if os.path.exists(pathname):
                shutil.copy2(pathname, dir2)
            continue
        # file in other sync then copy the latest of thw two to the other side
        # if a file has the same current digest in both directories but different modification dates
        elif filename in sync2:
            if latest_file_update_sync1[1] == sync2[filename][0][1]:
                copy_latest_file(dir1, dir2, filename, latest_file_update_sync1, sync2[filename][0])
            else:
                # check that all hashes are different
                file_moved_boolean = False
                for sync2_file_arrays in sync2[filename]:
                    if latest_file_update_sync1[1] == sync2_file_arrays[1]:
                        # file in dir2 must be newer
                        pathname = os.path.join(dir2, filename)
                        if os.path.exists(pathname):
                            shutil.copy2(pathname, dir1)
                        file_moved_boolean = True
                        break
                    if not file_moved_boolean:
                        for sync1_file_arrays in sync1[filename]:
                            if sync2[filename][0][1] == sync1_file_arrays[1]:
                                # file in dir1 must be newer
                                pathname = os.path.join(dir1, filename)
                                if os.path.exists(pathname):
                                    shutil.copy2(pathname, dir2)
                                break
                    # we get here only if both digests are unique
                    # if a file has different digests in both directories then the files are different, copy over latest (not ideal)
                    copy_latest_file(dir1, dir2, filename, latest_file_update_sync1, sync2[filename][0])

    # finally copy over files in the second sync that are not in the first
    for filename in sync2.keys():
        if filename not in sync1 and sync2[filename][0][1] != "deleted":
            pathname = os.path.join(dir2, filename)
            if os.path.exists(pathname):
                shutil.copy2(pathname, dir1)


def copy_latest_file(dir1, dir2, filename, latest_file_update_sync1, latest_file_update_sync2):
    if repr(latest_file_update_sync1[0]) > repr(latest_file_update_sync2[0]):
        pathname = os.path.join(dir1, filename)
        if os.path.exists(pathname):
            shutil.copy2(pathname, dir2)
    else:
        pathname = os.path.join(dir2, filename)
        if os.path.exists(pathname):
            shutil.copy2(pathname, dir1)


"""
@function
Recursive function that calls main with inputs as the new child folders
"""


if __name__ == "__main__":
    if len(sys.argv) != 3 or (not os.path.isdir(sys.argv[1]) and not os.path.isdir(sys.argv[2])) :
        print("Usage: sync directory1 directory2")
        exit()
    main(sys.argv[1], sys.argv[2])
