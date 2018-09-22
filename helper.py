"""
Helper functions

Created by Weida Zhong, on 08/20/2018

Tested in Python 3.6
"""

import gzip
import sys,traceback
import os
import pickle

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
        The compress type (i.e. extension)
    """
    # TODO: handle exception FileNotFoundError properly
    global merge
    merge = False
    if (input_string == "syntax"):
        print("unzip [-f filename] [-d directory] [--compress-type='.zip'] [--delete=False] [--merge=True]. If --delete is set to be True, then the original compressed file(s) will be deleted after decompression. If --merge is True, then files with the same prefix will be merged after decompression.")
        return
    mypath = os.path.dirname(os.path.realpath(__file__))
    print(mypath)
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
    mypath = os.path.join(mypath,filename)
    subdirs = os.listdir(mypath)
    for subdir in subdirs:
        file_path = os.path.join(mypath,subdir+"/")
        subfiles = os.listdir(file_path)
        global data_lines
        data_lines = ""
        for fil in subfiles:
            if(os.path.isdir(fil)):
                decompress_file(fil)
            else:
                try:
                    fil = os.path.join(file_path,fil)
                    print(fil)
                    zip_file = gzip.open(fil)
                    data_lines = zip_file.readlines()
                    uncompressed_filename = fil[:-len(compress_type)]
                    with open(uncompressed_filename, "wb") as fp:
                        fp.writelines(data_lines)
                    print(delete_after_decompress)
                    if (delete_after_decompress):
                        print("deleting ",fil) 
                        fil = os.path.join(mypath,fil)
                        os.remove(fil)
                except:
                    pass
    #Merge files
    if(merge):
        subdirs = os.listdir(mypath)
        for subdir in subdirs:
            file_path = os.path.join(mypath,subdir)
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
                lines = []
                for fil in acc:
                    file_name = os.path.join(file_path,fil)
                    file_data = open(file_name).readlines()
                    lines.extend(file_data)
                    os.remove(file_name)    
                uncompressed_filename = "raw_acc.txt"
                uncompressed_filename = os.path.join(file_path,uncompressed_filename)
                with open(uncompressed_filename, "wb") as fp:
                    print("Created",uncompressed_filename)
                    print(type(lines))
                    pickle.dump(lines, fp)
            if(obd):
                lines = []
                for fil in obd:
                    file_name = os.path.join(file_path,fil)
                    file_data = open(file_name).readlines()
                    lines.extend(file_data)
                    os.remove(file_name)     
                uncompressed_filename = "raw_obd"
                with open(uncompressed_filename, "wb") as fp:
                    print("Created",uncompressed_filename)
                    pickle.dump(lines, fp) 
            if(gyro):
                lines = []
                for fil in gyro:
                    file_name = os.path.join(file_path,fil)
                    lines.extend(open(file_name).readlines())
                    os.remove(file_name)     
                uncompressed_filename = "raw_gyro"
                with open(uncompressed_filename, "wb") as fp:
                    print("Created",uncompressed_filename)
                    pickle.dump(lines, fp) 
            if(mag):
                lines = []
                for fil in mag:
                    file_name = os.path.join(file_path,fil)
                    lines.extend(open(file_name).readlines())
                    os.remove(file_name)   
                uncompressed_filename = "raw_mag"
                with open(uncompressed_filename, "wb") as fp:
                    print("Created",uncompressed_filename)
                    pickle.dump(lines, fp)     