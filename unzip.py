"""
Helper functions

Created by Weida Zhong, on 08/20/2018

Tested in Python 3.6
"""

import gzip
import sys
import traceback
import os
import pickle
from collections import defaultdict
# import textwrap

from utils import convert_to_map


def decompress_file(input_string):
    """
    Decompress a given file. Generate a new file within the same address,
    with the same file name without compress extension.
    """
    # TODO: handle exception FileNotFoundError properly
    if input_string == "syntax":
        info = """unzip [-f filename] [-d directory] [--compress-type='.zip'] [--delete=False] [--merge=True] [--delete-unzip=True].
          filename has to include the full path.
          If --delete is set to be True, then the original compressed file(s) will be deleted after decompression.
          If --merge is "rue, then files with the same prefix will be merged after decompression.
          if --delete-unzip is True, then uncompressed files will be deleted after merge."""
        # wrapper = textwrap.TextWrapper(width=70)
        # print(wrapper.fill(info))
        print(info)
        return
    mypath = os.path.dirname(os.path.realpath(__file__))

    options = convert_to_map(input_string)

    dirname = options.get('-d', None)
    filename = options.get('-f', None)

    if not filename and not dirname:
        print("error: either filename or directory is needed")
        return

    if filename and dirname:
        print("error: cannot take both filename and directory at the same time.")
        return

    compress_type = options.get('--compress-type', '.zip')
    delete_after_decompress = options.get('--delete', "False")
    delete_unzip = options.get('--delete-unzip', "True")
    merge = options.get('--merge', "True")

    if filename:
        unzip_file(filename, delete_after_decompress, compress_type)
        return
    mypath = dirname
    process_directory(mypath, delete_after_decompress, compress_type)
    # Merge files
    if merge == "True":
        merge_directories(mypath, delete_unzip)


def merge_directories(mypath, delete_unzip):
    """
    Merge the uncompressed files within each directory.

    Parameters
    ----------
    mypath : str
        The folder to deal with

    delete_unzip : str, "True" or "False"
        If "True", uncompressed files will be deleted after merge
    """
    for root, subdirs, _ in os.walk(mypath):
        # only deal with folder without subfolders
        if len(subdirs) == 0:  # TODO: this can be removed if needed
            merge_single_directory(root, delete_unzip)


def process_directory(mypath, delete_after_decompress, compress_type):
    """
    unzip all files under given directionry and all its sub directories

    Parameters
    ----------
    mypath : str
        The folder (full path) to be dealt with

    delete_after_decompress : str, "True" or "False"
        If "True", then original compressed files will be deleted after unzip

    compress_type : str
        The extension for the compressed files.
    """
    for root, _, files in os.walk(mypath):
        for fil in files:
            if not fil.endswith(compress_type):
                continue
            # TODO: only deal with certain type of data that we are interested
            fil = os.path.join(root, fil)
            unzip_file(fil, delete_after_decompress, compress_type)


def unzip_file(fil, delete_after_decompress, compress_type):
    """
    unzip a single file.

    Parameters
    ----------
    fil : str
        The full path of the file to be uncompressed

    delete_after_decompress : str, "True" or "False"
        If "True", then delete the original compressed file after unzip

    compress_type : str
        The extension of the compressed file
    """
    if not os.path.isfile(fil):
        print("unzip_file: ERROR: file %s does NOT exist" % fil)
        return
    try:
        zip_file = gzip.open(fil)
        data_lines = zip_file.readlines()
        uncompressed_filename = fil[:-len(compress_type)]
        with open(uncompressed_filename, "wb") as fp:
            fp.writelines(data_lines)

        if (delete_after_decompress == "True"):
            print("deleting ", fil)
            os.remove(fil)
        else:
            print("delete after unzip: ", delete_after_decompress)
    except:
        print("exception happens in unzip %s" % fil)
        pass


def merge_single_directory(file_path, delete_unzip):
    """
    Merge files with same prefix under the given path.
    Assuming there is NO sub folder within this path.

    Parameters
    ----------
    file_path : str
        Folder to deal with

    delete_unzip : str, 'True' or 'False'
        If 'True', uncompressed files will be deleted after merge.
    """
    subfiles = os.listdir(file_path)

    data_type = ['acc', 'obd', 'gps', 'gyro', 'mag']
    file_extension = '.txt'

    uncompressed_files_dict = defaultdict(list)
    for fil in subfiles:
        file_name = os.path.basename(fil)  # TODO: this is not necessary since subfiles are just file names
        if not file_name.endswith(file_extension):
            continue
        for prefix in data_type:
            if prefix in file_name:
                uncompressed_files_dict[prefix].append(file_name)
                break

    for prefix, files in uncompressed_files_dict.items():
        files = sorted(files)
        all_lines = []
        for f in files:
            file_name = os.path.join(file_path, f)
            with open(file_name, 'rb') as fp:
                all_lines.extend(fp.readlines())
            if delete_unzip == "True":
                os.remove(file_name)
        if prefix == 'gps':
            merged_file = os.path.join(file_path, prefix + ".txt")
        else:
            merged_file = os.path.join(file_path, "raw_" + prefix + ".txt")
        with open(merged_file, 'wb') as fp:
            fp.writelines(all_lines)
