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
        compress_type = input_string[3].split("=")[1]
        delete_after_decompress = input_string[4].split("=")[1]
        merge = input_string[5].split("=")[1]
    elif(len(input_string) == 5):
        filename = input_string[2]
        if("compress-type" in (input_string[3].split("=")[0])):
            compress_type = input_string[3].split("=")[1]
            if((input_string[4].split("=")[0]) == "--delete"):
                delete_after_decompress = input_string[4].split("=")[1]
                print("delete_after_decompress",delete_after_decompress)
            elif((input_string[4].split("=")[0]) == "--merge"):
                merge = input_string[4].split("=")[1]
        elif("delete" in (input_string[3].split("=")[0])):
            delete_after_decompress = input_string[3].split("=")[1]
            print("delete_after_decompress",delete_after_decompress)
            merge = input_string[4].split("=")[1]
            compress_type = ".zip"
    elif(len(input_string) == 4):
        filename = input_string[2]
        if("compress" in input_string[3].split("=")[0]):
            compress_type = input_string[3].split("=")[1]
            delete_after_decompress = False
            merge = False
        elif("merge" in input_string[3].split("=")[0]):
            print(input_string[3].split("=")[1])
            delete_after_decompress = input_string[3].split("=")[1]
            compress_type = ".zip"
            merge = False
        else:
            compress_type = ".zip"
            delete_after_decompress = True
            merge = input_string[3].split("=")[1]  
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
                    with open(uncompressed_filename, "wb") as fp:
                        fp.writelines(lines)
                    print(delete_after_decompress)
                    if (delete_after_decompress):
                        print("deleting ",fil) 
                        fil = os.path.join(mypath,fil)
                        os.remove(fil)
                except:
                    traceback.print_exc(file=sys.stdout)
                    print ("File not found. Please check the file name properly.")
    #Merge files
    if(merge):
        for subdir in subdirs:
            file_path = os.path.join(mypath,subdir+"/")
            subfiles = os.listdir(file_path)
            for fil in subfiles:
                    file_name = os.path.basename(fil)
                    acc = []
                    obd = []
                    gyro = []
                    mag = []
                    if "raw_acc" in file_name and "zip" not in file_name:
                        acc.append(file_name)
                    elif "raw_obd" in file_name and "zip" not in file_name:
                        obd.append(file_name)
                    elif "raw_gyro" in file_name and "zip" not in file_name:
                        gyro.append(file_name)
                    elif "raw_mag" in file_name and "zip" not in file_name:
                        mag.append(file_name)
                    if(acc):
                        lines = ""
                        for fil in acc:
                            fil = os.path.join(file_path,fil)
                            lines.append(open(fil).readlines())
                            os.remove(fil)    
                        uncompressed_filename = "raw_acc"
                        with open(uncompressed_filename, "wb") as fp:
                            fp.writelines(lines) 
                    if(obd):
                        lines = ""
                        for fil in obd:
                            fil = os.path.join(file_path,fil)
                            lines.append(open(fil).readlines())
                            os.remove(fil)     
                        uncompressed_filename = "raw_obd"
                        with open(uncompressed_filename, "wb") as fp:
                            fp.writelines(lines) 
                    if(gyro):
                        lines = ""
                        for fil in gyro:
                            fil = os.path.join(file_path,fil)
                            lines.append(open(fil).readlines())
                            os.remove(fil)     
                        uncompressed_filename = "raw_gyro"
                        with open(uncompressed_filename, "wb") as fp:
                            fp.writelines(lines) 
                    if(mag):
                        lines = ""
                        for fil in mag:
                            fil = os.path.join(file_path,fil)
                            lines.append(open(fil).readlines())
                            os.remove(fil)   
                        uncompressed_filename = "raw_mag"
                        with open(uncompressed_filename, "wb") as fp:
                            fp.writelines(lines)     