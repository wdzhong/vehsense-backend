"""
Helper functions

Created by Weida Zhong, on 08/20/2018

Tested in Python 3.6
"""

import gzip
import sys,traceback
import os


def decompress_file(input_string):
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
    mypath = "/media/anurag/UbuntuProjects/VehSense-Dev/"
    filename = ""
    if(len(input_string) == 6):
        filename = input_string[2]
        compress_type = input_string[3]
        delete_after_decompress = input_string[4]
        merge = input_string[5]
    elif(len(input_string) == 5):
        filename = input_string[2]
        compress_type = input_string[3]
        delete_after_decompress = input_string[4]
        merge = False  
    elif(len(input_string) == 4):
        filename = input_string[2]
        compress_type = input_string[3]
        delete_after_decompress = False
        merge = False
    elif(len(input_string) == 3):
        filename = input_string[2]
        compress_type = ".zip"
        delete_after_decompress = False
        merge = False
    else:
        print ("Please check syntax")
        return
    mypath = mypath + filename
    subdirs = os.listdir(mypath)
    for subdir in subdirs:
        file_path = os.path.join(mypath,subdir+"/")
        print("file_path")
        print(file_path)
        subfiles = os.listdir(file_path)
        global lines
        lines = ""
        for fil in subfiles:
            if(os.path.isdir(fil)):
                decompress_file(fil)
            else:
                try:
                    fil = os.path.join(file_path,fil)
                    print(fil)
                    zip_file = gzip.open(fil)
                    lines = zip_file.readlines()
                    uncompressed_filename = fil[:-len(compress_type)]
                    print(uncompressed_filename)
                    with open(uncompressed_filename, "wb") as fp:
                        fp.writelines(lines)
                    if (delete_after_decompress == True):
                        fil = os.path.join(mypath,fil)
                        os.remove(fil)
                except:
                    traceback.print_exc(file=sys.stdout)
                    print ("File not found. Please check the file name properly.")
