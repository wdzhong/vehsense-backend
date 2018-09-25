
"""
The entrance of the project.
TODO: docstring with more details

Create by Weida Zhong, on July 02 2018
version 1.0
Python 3.x

"""

import textwrap
import sys
import shutil
import os
import time
from datetime import datetime
from dateutil import tz
from time import gmtime,strftime
from helper import decompress_file

parent_path = os.path.dirname(os.path.realpath(__file__)) #Parent directory of VehSense data
data_path = os.path.join(parent_path,"vehsense-backend-data") #VehSense data directory
temp_path = os.path.join(parent_path,"vehsense-backend-data-temp") #temporary folder for storing the data after clean if -f is specified
backup_path = os.path.join(parent_path,"vehsense-backend-data-backup") # path of backup folder

def sub_dir_path (d):
    """
    Filters directories from the argument directory and returns the list of sub-directory folders.

    Args:
        d (str): directory of data
        
    Returns:
        List of sub-directories in the given directory.
        
    """
    return filter(os.path.isdir,[os.path.join(d,f) for f in os.listdir(d)])
   
def helper():
    """
    Displays the functions of individual commands. This is invoked when user enters "help" in the command-line.
       
    """    
    print("Usage: \"help [cmd]\" for function syntax.\n")
    print("These are the VehSense commands used for various tasks:\n")    
    cmd_list = {1: "help cmd", 2: "clean", 3: "size", 4: "new", 5: "backup" ,6: "exit",7: "unzip"}
    vehSenseCommands = {"clean": "move 'bad' trip (based on the input criteria) to a \
temporary location for manual inspection before moving to trash.\
 Move to trash immediately if [-f] is used."}
    vehSenseCommands["help cmd"] = "displays the syntax and description for the command."
    vehSenseCommands["size"] = "display overall size, and size for each user"
    vehSenseCommands["new"] = "show newly added data since last time running this command or specified time point"
    vehSenseCommands["backup"] = "backup data. Ask for backup location if [-d] is not specified, and save it for future use."
    vehSenseCommands["exit"] = "exits VehSense backend."
    vehSenseCommands["unzip"] = "decompress the specified file, or compressed files under specified directory."
    for i in range(len(cmd_list)):
        command = cmd_list[i + 1]
        prefix = " "
        preferredWidth = 100
        wrapper = textwrap.TextWrapper(initial_indent = prefix, width = preferredWidth,subsequent_indent = ' '*10)   
        print ("{:<8} {:<15}".format(command, wrapper.fill(vehSenseCommands[command])))
          
def clean_file(input_string):
    """
    Performs the operations for the clean command, i.e, moves the files to a temporary folder or moves them to trash depending on the minimum size specified.

    Args:
        input_string (str array): options for clean command, along with the "clean" option.      

    """
    if(input_string == "syntax"):
        print("clean [-acc] min_size_of_acc [-gps] min_size_of_gps [-gyro] min_size_of_gyro [-obd] min_size_of_obd [-grav] min_size_of_grav [-mag] min_size_of_mag [-rot] min_size_of_rot [--all] min_size_of_file [-f]")
    else:
        move_trash = False
        flag = False
    
        for i,val in enumerate(input_string):
            if (flag == True):
                flag = False
                continue
            if (val == "clean"):
                if(len(input_string) != 1):
                    continue
                else:
                    print("Enter correct options")
                    return
            if(input_string[len(input_string)-1] == "-f"):
                move_trash =  True
            if(val == "--all"):
                size = int(input_string[i+1])
                flag = True
                clean_all(move_trash,size)
            elif((val == "-acc") or (val == "-gps") or (val == "-gyro") or (val == "-obd") or (val == "-grav") or (val == "-mag") or (val == "-rot")):
                try:
                    size = int(input_string[i+1])
                    flag = True
                    clean_subfile(val[1:],size,move_trash)
                except:
                    print("Enter correct options")
                    return
            elif(val == "-f"):
                continue
            else:
                print("Enter the correct options")
                return
        
def clean_subfile(filetype,size,move_trash):
    """
    Performs the clean operations of the individual files, invoked from within the clean_file method.

    Args:
        filetype (str): type of file, ex: acc, obd, gps, grav.
        size (int): the threshold size of files in bytes.
        move_trash (bool): true if the files need to move to trash.
    
    """
    switcher = {"acc": "raw_acc.txt", "obd": "raw_obd.txt", "gps": "gps.txt", "gyro": "raw_gyro.txt", "grav": "raw_grav.txt", "mag": "raw_mag.txt", "rot": "raw_rot.txt"}
    filename = switcher[filetype]
    for subdir in sub_dir_path(data_path):
        subdirs = sub_dir_path(subdir)
    for subdir_datewise in subdirs:
        raw_file = os.path.join(data_path,filename)
        if(os.path.exists(raw_file)):
            if((os.stat(raw_file).st_size) <= size):
                if (move_trash == True):
                    print("Deleting file ",raw_file)
                    os.remove(raw_file)
                else:
                    print ("Moving file ",raw_file)
                    source = subdir_datewise
                    dest1 = os.path.basename(subdir_datewise)
                    dest2 = os.path.basename(os.path.dirname(subdir_datewise))
                    dest_f1 = os.path.join(temp_path,dest2)
                    dest_f2= os.path.join(dest_f1,dest1)
                    if not os.path.exists(dest_f2):
                        os.makedirs(dest_f2)
                    shutil.move(source+"/"+filename,dest_f2)
        
def clean_all(move_trash,size):
    """
    Performs the clean operations of the individual files, invoked from within the clean_file method.

    Args:
        move_trash (bool): true if the files need to move to trash.
        size (int): the threshold size of files in bytes.

    """
    for subdir in sub_dir_path(data_path):
        subdirs = sub_dir_path(subdir)
        for subdir_datewise in subdirs:
            sub_path = os.path.join("",subdir_datewise)
            for root, subdirs, files in os.walk(sub_path):
                for filename in files:
                    raw_file = os.path.join(subdir_datewise,filename)
                    if((os.stat(raw_file).st_size) <= size):
                        if (move_trash == True):
                            os.remove(raw_file)
                        else:
                            source = subdir_datewise
                            dest1 = os.path.basename(subdir_datewise)
                            dest2 = os.path.basename(os.path.dirname(subdir_datewise))
                            dest_f1 = os.path.join(temp_path,dest2)
                            dest_f2= os.path.join(dest_f1,dest1)
                            if not os.path.exists(dest_f2):
                                os.makedirs(dest_f2)
                            shutil.move(source+"/"+filename,dest_f2)
         
def backup(input_string):
    """
    Performs the operations for the backup command, i.e, moves the files to the backup location if not specified.

    Args:
        input_string (str array): array of options for backup command.

    """
    if(input_string == "syntax"):
        print("backup [-d] [directory] ")
    else:
        if (len(input_string) == 1):
            print ()
            print ("Is this the correct backup location? (Enter \"Yes\"/\"No\").")
            print ("Enter \"main\" to go back to main")
            print (backup_path)
            option = input(">>")
            if (option == "N" or option =="No"  or option =="no" or option == "NO"):
                print("Enter the backup location")
                global backup_path
                backup_path = input(">>")
            elif (option == "Y" or option =="Yes"  or option =="yes" or option =="YES"):
                pass
            elif (option == "main"):
                return
            elif (option == "exit"):
                print ("Exiting VehSense backend.")
                sys.exit()        
            else:
                print ("Please enter correct input.")
                backup(input_string)
                return
        elif (len(input_string) == 3):
            if(input_string[1] == "-d"):
                backup_path = input_string[2]
            else:
                print ("Enter the correct option")
                input_string = ["backup"]
                backup(input_string)
                return
        else:
            print ("Enter the correct options")
            input_string = ["backup"]
            backup(input_string)
            return
        print("Copying following files to backup location:")
        for subdir in sub_dir_path(data_path):
            subdirs = sub_dir_path(subdir)
            for subdir_datewise in subdirs:
                    sub_path = os.path.join("",subdir_datewise)
                    for root, subdirs, files in os.walk(sub_path):
                        for filename in files:
                            raw_file = os.path.join(subdir_datewise,filename)
                            print(raw_file)
                            source = subdir_datewise
                            dest1 = os.path.basename(subdir_datewise)
                            dest2 = os.path.basename(os.path.dirname(subdir_datewise))
                            dest_f1 = os.path.join(backup_path,dest2)
                            dest_f2 = os.path.join(dest_f1,dest1)
                            if not os.path.exists(dest_f2):
                                os.makedirs(dest_f2)
                            shutil.copy(source+"/"+filename,dest_f2)
        print ()
        print ("Backup complete.")

def new(input_string):
    """
    Performs the operations for the new command, i.e, displays the list of files which were created after last running the command.

    Args:
        input_string (str): array of options for the new command.

    """
    if(input_string == "syntax"):
        print("new -t [YYYY-MM-DD HH:MM:SS] to display the files created after the provided time")
    else:
        pattern = '%Y-%m-%d %H:%M:%S-04:00'
        pattern1 = '%Y-%m-%d %H:%M:%S'
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('America/New_York')
    
        if (len(input_string) == 1):
            my_file = open(os.path.join(parent_path,"new_time.txt"),"r")
            specified_time = my_file.read()
            my_file.close()
        elif (len(input_string) != 4):
            print("Please enter correct syntax")
            return
        else:
            specified_time = input_string[2]+" "+input_string[3]
        with open(os.path.join(parent_path,"new_time.txt"),"w") as my_file:
            utc = datetime.utcnow()
            utc = str(utc).split(".")[0]
            utc = datetime.strptime(utc, '%Y-%m-%d %H:%M:%S')
            utc = utc.replace(tzinfo=from_zone)
            central =str(utc.astimezone(to_zone))
            my_file.write(central)
            my_file.close()
        try:
            epoch = float(time.mktime(time.strptime(specified_time, pattern1)))
        except:
            print ("Error in parsing time. Please check syntax.")
            return
        print("Data created after " + specified_time)
        for subdir in sub_dir_path(data_path):
            subdirs = sub_dir_path(subdir)
            print(" ")
            dest1 = os.path.basename(subdir)
            print("User ",dest1)
            for subdir_datewise in subdirs:
                sub_path = os.path.join("",subdir_datewise)                
                for root, subdirs, files in os.walk(sub_path):
                    for filename in files:
                        raw_file = os.path.join(subdir_datewise,filename)
                        if(os.path.getmtime(raw_file) > epoch):
                            print(raw_file)
                        
def cmd_help(cmd):
    """
    Performs the operations for the "help cmd" command, i.e, displays the syntax of individual commands.

    Args:
        input_string (str): array of options for the new command.

    """
    print()
    func_list = {"clean": clean_file, "size": size, "new": new, "backup": backup, "unzip": decompress_file}
    vehSenseCommands = {"clean": "move 'bad' trip (based on the input criteria) to a\
temporary location for manual inspection before moving to trash.\
 Move to trash immediately if -f is used. Atleast one option needs to be specified."}
    vehSenseCommands["size"] = "display overall size, and size for each user"
    vehSenseCommands["new"] = "show newly added data since last time running this command or specified time point"
    vehSenseCommands["backup"] = "backup the files to the specified path and store the path for future use or backup the data to the stored path if [-d] is not specified."
    vehSenseCommands["exit"] = "exits VehSense backend."
    vehSenseCommands["unzip"] = "decompress the specified file, or compressed files under specified directory. If --delete is set to be True, then the original compressed file(s) will be deleted after decompression. If --merge is True, then files with the same prefix will be merged after decompression."
        
    if cmd not in func_list:
        print ("Unrecognized command. Enter \"help [cmd]\" for function syntax, \"help\" for list of available commands")
    else:
        print("Description:", vehSenseCommands[cmd],"\n")
        print("Usage:") 
        func_list[cmd]("syntax")

def get_size(start_path = '.'):
    """
    Calculates the size of file or directory.

    Args:
        start_path (str): path of file or directory.

    Returns:
        float: size of file or directory in KB.
        
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size/float(1000)

def size(cmd):
    """
    Performs the operations for the size command, i.e, displays the size of each user.

    Args:
        cmd (str): path of file or directory.
        
    """
    if(cmd == "syntax"):
        print("size")
    elif(len(cmd) != 1):
        print("Please enter correct syntax.")
    else:
        print(cmd)
        print("Overall size: ")
        print(get_size(data_path), "KB")
        for subdir in sub_dir_path(data_path):
            print(os.path.basename(subdir))
            print("size",get_size(subdir), "KB")
                        
def main():
    """
    Takes the user input and invokes the appropriate method.
        
    """
    print ("Welcome to Vehsense backend utility. Enter \"help\" for list of available commands.")
    switcher = {"clean": clean_file, "size": size, "new": new, "backup": backup, "unzip": decompress_file}    
    while True:
        inputString = input(">>").split(" ")
        receivedCmd = inputString[0]
        if receivedCmd == "help" and len(inputString) == 1:
            helper()
        elif receivedCmd == "help" and len(inputString) == 2:
            cmd_help(inputString[1])            
        elif receivedCmd == "exit":
            print ("Exiting VehSense backend.")
            sys.exit()    
        elif receivedCmd in switcher:
            type(inputString)
            switcher[receivedCmd](inputString)
        else:
            print ("Unrecognized command. Enter \"help [cmd]\" for function syntax, \"help\" for list of available commands")
    
if __name__ == '__main__':
    #TODO: accept parameters or prompt the user to input, e.g. directory of data
    main()