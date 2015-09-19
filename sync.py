#!/usr/bin/env python3
import sys
import os
import json

__author__ = 'Ofek'


def main():
    print(_dir1 + " " + _dir2)
    load_sync_json()
    load_files()


"""
@function
Load in the two folders and all their files, check if folders exist, if they do not, create the folders
"""


def load_files():
    if os.path.exists(_dir1):  # ie folder exists
        _dir1_filenames = os.listdir(_dir1)
        for filename in _dir1_filenames:
            pathname = os.path.join(_dir1, filename)
            print("current file is: " + pathname)
    else:
        # create folder
        os.makedirs(_dir1)

    if os.path.exists(_dir2):  # ie folder exists
        _dir2_filenames = os.listdir(_dir2)
        for filename in _dir2_filenames:
            pathname = os.path.join(_dir1, filename)
            print("current file is: " + pathname)
    else:
        # create folder
        os.makedirs(_dir2)


"""
@function
Generate SHA-256 digest and include modified times and deletes
"""

"""
@function
Generate sync file
"""

"""
@function
Read in sync file and or create it
"""


def load_sync_json():
    sync_dir1 = os.path.join(_dir1, ".sync")
    sync_dir2 = os.path.join(_dir2, ".sync")

    if os.path.isfile(sync_dir1):
        with open(sync_dir1) as json_file:
            _sync1 = json.load(json_file)
            print(_sync1)

    if os.path.isfile(sync_dir2):
        with open(sync_dir2) as json_file:
            _sync2 = json.load(json_file)
            print(_sync1)


"""
@function
Sync directories
"""

"""
@function
Recursive function that calls main with inputs as the new child folders
"""

if __name__ == "__main__":
    _dir1 = sys.argv[1]
    _dir2 = sys.argv[2]
    main()

""""
def __init__(self):
    main(sys.argv[1], sys.argv[2])
    self.dir11 = sys.argv[1]
    print(self.dir11)
    self.dir22 = sys.argv[2]
"""""
