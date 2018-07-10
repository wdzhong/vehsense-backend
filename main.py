"""
The entrance of the project.
TODO: docstring with more details

Create by Weida Zhong, on July 02 2018
version 1.0
Python 3.x
"""

def helper():
    print()
    cmd_list = {1:"help",2:"clean",3:"size",4:"clients",5:"new",6:"backup"}
    vehSenseCommands = {"help": "[cmd]: function usage"}
    vehSenseCommands["clean"]= "[-acc] [-gps] [-gyro] [-obd] [--all] [-f]]: move 'bad' trip (based on the input creteria) to a temporary location for manually inspection before moving to trash. Move to trash immediately if -f is used."  
    vehSenseCommands["size"] = ": overall size, and size for each user"
    vehSenseCommands["clients"] = ": list all clients' names"
    vehSenseCommands["new"]= "[-t time]: show newly added data since last time running this command or specified time point"
    vehSenseCommands["backup"]= "[-d directory]: backup data. Ask for backup location if -d is not specified, and save it for future use."
    for i in range(len(cmd_list)):
        command = cmd_list[i+1]
        print(command,vehSenseCommands[command])
        
if __name__ == '__main__':
    #TODO: accept parameters or prompt the user to input, e.g. directory of data
    print (">>Welcome to Vehsense backend utility. Enter \"help\" for list of available commands.")
    switcher = { "help":helper,"clean":helper,"size":helper,"clients":helper,"new":helper,"backup":helper}
    while True:
        inputString = input().split(" ")
        receivedCmd = inputString[0]
        if receivedCmd in switcher:
            switcher[receivedCmd]()                       
        else:
            print (">>Unrecognized command. Enter \"help\" for list of available commands.")
        