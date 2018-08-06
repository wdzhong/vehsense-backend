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
path = "/media/anurag/UbuntuProjects/VehSense-Dev/vehsense-backend-data"
backup_path = "/media/anurag/UbuntuProjects/VehSense-Dev/vehsense-backend-data-backup"

def sub_dir_path (d):
    """
    Filters directories from the argument directory and returns the list of sub-directory folders.

    Args:
        d : directory of data
        
    Returns:
        List of sub-directories in the given directory.
        
    """
    return filter(os.path.isdir,[os.path.join(d,f) for f in os.listdir(d)])
   
def helper():
    #TODO: Wrap the description of commands for display properly.
    print("Usage: \"help [cmd]\" for function usage. \"help --[cmd]\" for function syntax.\n")
    print("These are the VehSense commands used for various tasks:\n")    
    cmd_list = {1: "clean", 2: "size", 3: "clients", 4: "new", 5: "backup" ,6: "exit"}
    vehSenseCommands = {"clean": "move 'bad' trip (based on the input criteria) to a \
temporary location for manual inspection before moving to trash.\
 Move to trash immediately if [-f] is used."}
    vehSenseCommands["size"] = "display overall size, and size for each user"
    vehSenseCommands["clients"] = "list all clients' names"
    vehSenseCommands["new"] = "show newly added data since last time running this command or specified time point"
    vehSenseCommands["backup"] = "backup data. Ask for backup location if [-d] is not specified, and save it for future use."
    vehSenseCommands["exit"] = "exits VehSense backend."
    for i in range(len(cmd_list)):
        command = cmd_list[i + 1]
        prefix = " "
        preferredWidth = 100
        wrapper = textwrap.TextWrapper(initial_indent = prefix, width = preferredWidth,subsequent_indent = ' '*10)   
        print ("{:<8} {:<15}".format(command, wrapper.fill(vehSenseCommands[command])))


def clean(cmd):
    options = {}
    #Options list with mandatory value
    options["[-acc]"] = False
    options["[-gps]"] = False
    options["[-gyro]"] = False
    options["[-obd]"] = False
    options["[--all]"] = False
    options["[-f]"] = False
    if cmd == "options":
        print (options)
    elif cmd == "syntax":
        for i in options:
            print (i, end =",")
            

    
def clean_file(input_string):
    move_trash = False
    flag = False

    for i,val in enumerate(input_string):
        if (flag == True):
            flag = False
            continue
        if (val=="clean"):
            continue
        if(input_string[len(input_string)-1] == "-f"):
            move_trash =  True
        if(val == "-all"):
            size = int(input_string[i+1])
            flag = True
            clean_all(move_trash,size)
        else:
            print(i)
            size = int(input_string[i+1])
            flag = True
            clean_subfile(val[1:],size,move_trash)
        
def clean_subfile(filetype,size,move_trash):
    switcher = {"acc": "raw_acc.txt", "obd": "raw_obd.txt", "gps": "gps.txt", "gyro": "raw_gyro.txt", "grav": "raw_grav.txt", "mag": "raw_mag.txt", "rot": "raw_rot.txt"}
    filename = switcher[filetype]
    for subdir in sub_dir_path(path):
        subdirs = sub_dir_path(subdir)
    for subdir_datewise in subdirs:
        raw_file = os.path.join(subdir_datewise,filename)
        if(os.path.exists(raw_file)):
            print (os.stat(raw_file).st_size)
            if((os.stat(raw_file).st_size) <= size):
                if (move_trash == True):
                    os.remove(raw_file)
                else:
                    print (subdir_datewise)
                    source = subdir_datewise
                    dest1 = os.path.basename(subdir_datewise)
                    dest2 = os.path.basename(os.path.dirname(subdir_datewise))
                    dest_f1 = os.path.join(backup_path,dest2)
                    dest_f2= os.path.join(dest_f1,dest1)
                    if not os.path.exists(dest_f2):
                        os.makedirs(dest_f2)
                    shutil.move(source+"/"+filename,dest_f2)
        
def clean_all(move_trash,size):
    for subdir in sub_dir_path(path):
        subdirs = sub_dir_path(subdir)
    for subdir_datewise in subdirs:
        for root, subdirs, files in os.walk(subdir_datewise):
            for filename in files:
                raw_file = os.path.join(subdir_datewise,filename)
                print(raw_file)
                if((os.stat(raw_file).st_size) <= size):
                    if (move_trash == True):
                        os.remove(raw_file)
                    else:
                        print (subdir_datewise)
                        source = subdir_datewise
                        dest1 = os.path.basename(subdir_datewise)
                        dest2 = os.path.basename(os.path.dirname(subdir_datewise))
                        dest_f1 = os.path.join(backup_path,dest2)
                        dest_f2= os.path.join(dest_f1,dest1)
                        if not os.path.exists(dest_f2):
                            os.makedirs(dest_f2)
                        shutil.move(source+"/"+filename,dest_f2)
    
            
def cmd_help(cmd):
    print()
    func_list = {"clean": clean, "size": helper, "clients": helper, "new": helper, "backup": helper, "exit": exit}
    vehSenseCommands = {"clean": "move 'bad' trip (based on the input criteria) to a\
temporary location for manual inspection before moving to trash.\
 Move to trash immediately if -f is used. Atleast one option needs to be specified."}
    vehSenseCommands["size"] = "display overall size, and size for each user"
    vehSenseCommands["clients"] = "list all clients' names"
    vehSenseCommands["new"] = "show newly added data since last time running this command or specified time point"
    vehSenseCommands["backup"] = "backup data. Ask for backup location if -d is not specified, and save it for future use."
    vehSenseCommands["exit"] = "exits VehSense backend."
        
    if cmd not in func_list:
        print ("Unrecognized command. Enter \"help --[cmd]\" for function syntax, \"help\" for list of available commands")
    else:
        print("Description:", vehSenseCommands[cmd],"\n")
        print("Options:") 
        func_list[cmd]("syntax")
        
def main():
    print ("Welcome to Vehsense backend utility. Enter \"help\" for list of available commands.")
    switcher = {"help": cmd_help, "clean": clean_file, "size": helper, "clients": helper, "new": helper, "backup": helper, "exit": exit}
    while True:
        inputString = input(">>").split(" ")
        receivedCmd = inputString[0]
        if receivedCmd == "help" and len(inputString) == 1:
            helper()
        elif receivedCmd == "help" and len(inputString) == 2:
            switcher[receivedCmd](inputString[1])            
        elif receivedCmd == "exit":
            print ("Exiting VehSense backend.")
            sys.exit()    
        elif receivedCmd in switcher:
            type(inputString)
            switcher[receivedCmd](inputString)
        else:
            print ("Unrecognized command. Enter \"help --[cmd]\" for function syntax, \"help\" for list of available commands")
    
if __name__ == '__main__':
    #TODO: accept parameters or prompt the user to input, e.g. directory of data
    main()