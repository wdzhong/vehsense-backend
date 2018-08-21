"""
Helper functions

Created by Weida Zhong, on 08/20/2018

Tested in Python 3.6
"""

import gzip


def decompress_file(filename, delete_after_decompress=False, compress_type="zip"):
    """
    Decompress a given file. Generate a new file within the same address,
    with the same file name without compress extension.

    Parameters
    ----------
    filename : str
        The name (absolute path) of the file to be decompressed

    delete_after_decompress : boolean, default=False
        If True, then delete the compressed file after decompression. Otherwise, keep it.

    compress_type : str, default="zip"
        The compress type (i.e. extention)
    """
    # TODO: handle exception FileNotFoundError properly
    zip_file = gzip.open(filename)
    lines = zip_file.readlines()

    uncompressed_filename = filename[:-len(compress_type)-1]
    with open(uncompressed_filename, "wb") as fp:
        fp.writelines(lines)
