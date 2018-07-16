"""
The entrance of the project.
TODO: docstring with more details

Create by Weida Zhong, on July 02 2018
version 1.0
Python 3.x
"""
import textwrap
import sys

def helper():
    #TODO: Wrap the description of commands for display properly.
    print("Usage: \"help [cmd]\" for function usage. \"help --[cmd]\" for function syntax.\n")
    print("These are the VehSense commands used for various tasks:\n")    
    cmd_list = {1: "clean", 2: "size", 3: "clients", 4: "new", 5: "backup"}
    vehSenseCommands = {"clean": "move 'bad' trip (based on the input criteria) to a \
temporary location for manual inspection before moving to trash.\
 Move to trash immediately if [-f] is used."}
    vehSenseCommands["size"] = "display overall size, and size for each user"
    vehSenseCommands["clients"] = "list all clients' names"
    vehSenseCommands["new"] = "show newly added data since last time running this command or specified time point"
    vehSenseCommands["backup"] = "backup data. Ask for backup location if [-d] is not specified, and save it for future use."
    for i in range(len(cmd_list)):
        command = cmd_list[i + 1]
        prefix = command + " "
        preferredWidth = 100
        wrapper = textwrap.TextWrapper(initial_indent = prefix, width = preferredWidth,subsequent_indent = ' '*9)   
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
    switcher = {"help": cmd_help, "clean": clean, "size": helper, "clients": helper, "new": helper, "backup": helper, "exit": exit}
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
            switcher[receivedCmd]()
        else:
            print ("Unrecognized command. Enter \"help --[cmd]\" for function syntax, \"help\" for list of available commands")
    
if __name__ == '__main__':
    #TODO: accept parameters or prompt the user to input, e.g. directory of data
    main()