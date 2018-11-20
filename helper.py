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
        compress_type = compress_type[1:-1]
        delete_after_decompress = input_string[4].split("=")[1]
        merge = input_string[5].split("=")[1]
    elif(len(input_string) == 5):
        filename = input_string[2]
        if("compress-type" in (input_string[3].split("=")[0])):
            compress_type = input_string[3].split("=")[1]
            compress_type = compress_type[1:-1]
            if("delete" in input_string[4].split("=")[0]):
                delete_after_decompress = input_string[4].split("=")[1]
                merge = False
                print("delete_after_decompress",delete_after_decompress)
            elif("merge" in input_string[4].split("=")[0]):
                delete_after_decompress = False
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
            compress_type = compress_type[1:-1]            
            delete_after_decompress = False
            merge = False
        elif("delete" in input_string[3].split("=")[0]):
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
        if subdir.startswith('.'):
            continue
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
                    zip_file = gzip.open(fil)
                    data_lines = zip_file.readlines()
                    print(fil)
                    uncompressed_filename = fil[:-len(compress_type)]
                    with open(uncompressed_filename, "wb") as fp:
                        fp.writelines(data_lines)
                    print(delete_after_decompress)
                    if (delete_after_decompress == "True"):
                        print("deleting ",fil) 
                        fil = os.path.join(mypath,fil)
                        os.remove(fil)
                except:
                    pass
    #Merge files
    if(merge == "True"):
        subdirs = os.listdir(mypath)
        for subdir in subdirs:
            if subdir.startswith('.'):
                continue
            file_path = os.path.join(mypath,subdir)
            subfiles = os.listdir(file_path)
            acc = []
            obd = []
            gyro = []
            mag = []
            gps = []
            for fil in subfiles:
                    file_name = os.path.basename(fil)
                    if "raw_acc" in file_name and "zip" not in file_name:
                        acc.append(file_name)
                    elif "raw_obd" in file_name and "zip" not in file_name:
                        obd.append(file_name)
                    elif "raw_gyro" in file_name and "zip" not in file_name:
                        gyro.append(file_name)
                    elif "raw_mag" in file_name and "zip" not in file_name:
                        mag.append(file_name)
                    elif "gps" in file_name and "zip" not in file_name:
                        gps.append(file_name)                                    
            acc = sorted(acc)        
            gyro = sorted(gyro)
            mag = sorted(mag)
            obd = sorted(obd)
            gps = sorted(gps)
            print(acc)
            print(gyro)
            print(mag)
            print(obd)                                                            
            print(gps)
                        
            if(acc):
                lines = []
                for fil in acc:
                    file_name = os.path.join(file_path,fil)
                    file_data = open(file_name)
                    lines.extend(file_data.readlines())
                    os.remove(file_name)    
                uncompressed_filename = "raw_acc.txt"
                uncompressed_filename = os.path.join(file_path,uncompressed_filename)
                with open(uncompressed_filename, 'w') as filehandle:  
                    print("Created",uncompressed_filename)
                    filehandle.writelines("%s" % place for place in lines)
                    
            if(obd):
                lines = []
                for fil in obd:
                    file_name = os.path.join(file_path,fil)
                    file_data = open(file_name).readlines()
                    lines.extend(file_data)
                    os.remove(file_name)     
                uncompressed_filename = "raw_obd.txt"
                uncompressed_filename = os.path.join(file_path,uncompressed_filename)
                with open(uncompressed_filename, "w") as fp2:
                    print("Created",uncompressed_filename)
                    fp2.writelines("%s" % place for place in lines)
            if(gyro):
                lines = []
                for fil in gyro:
                    file_name = os.path.join(file_path,fil)
                    file_data = open(file_name)
                    lines.extend(file_data.readlines())
                    file_data.close
                    os.remove(file_name)     
                uncompressed_filename = "raw_gyro.txt"
                uncompressed_filename = os.path.join(file_path,uncompressed_filename)
                with open(uncompressed_filename, "w") as fp3:
                    print("Created",uncompressed_filename)
                    fp3.writelines("%s" % place for place in lines) 
            if(mag):
                lines = []
                for fil in mag:
                    file_name = os.path.join(file_path,fil)
                    lines.extend(open(file_name).readlines())
                    os.remove(file_name)   
                uncompressed_filename = "raw_mag.txt"
                uncompressed_filename = os.path.join(file_path,uncompressed_filename)
                with open(uncompressed_filename, "w") as fp4:
                    print("Created",uncompressed_filename)
                    fp4.writelines("%s" % place for place in lines)
            if(gps):
                lines = []
                for fil in gps:
                    file_name = os.path.join(file_path,fil)
                    lines.extend(open(file_name).readlines())
                    os.remove(file_name)   
                uncompressed_filename = "gps.txt"
                uncompressed_filename = os.path.join(file_path,uncompressed_filename)
                with open(uncompressed_filename, "w") as fp5:
                    print("Created",uncompressed_filename)
                    fp5.writelines("%s" % place for place in lines)   