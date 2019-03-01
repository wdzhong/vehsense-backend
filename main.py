"""
The entrance of the project.
TODO: docstring with more details

Create by Weida Zhong, on July 02 2018
version 1.0
Python 3.x
"""

import textwrap
import sys
import os
import argparse

from unzip import decompress_file
from clean import clean_file
from preprocess import preprocess
from backup import backup
from size_cmd import size_cmd
from new_cmd import new_cmd


debug = True

vehSenseCommands = {"clean": "move 'bad' trip (based on the input criteria) to a temporary location for manual inspection before moving to trash. Move to trash immediately if [-f] is used."}
vehSenseCommands["help cmd"] = "displays the syntax and description for the command."
vehSenseCommands["size"] = "display overall size, and size for each user"
vehSenseCommands["new"] = "show newly added data since last time running this command or specified time point"
vehSenseCommands["backup"] = "backup data. Ask for backup location if [-d] is not specified, and save it for future use."
vehSenseCommands["exit"] = "exits VehSense backend."
vehSenseCommands["unzip"] = "decompress the specified file, or compressed files under specified directory."
vehSenseCommands["preprocess"] = "preprocess the files in the specified directory."

cmd_list = {"clean": clean_file, "size": size_cmd, "new": new_cmd,
            "backup": backup, "unzip": decompress_file, "preprocess": preprocess}


def helper():
    """
    Displays the functions of individual commands. This is invoked when user enters "help" in the command-line.
    """
    print("Usage: \"help [cmd]\" or simply \"cmd\" for function syntax.\n")
    print("These are the VehSense commands used for various tasks:\n")

    longest_cmd = max(cmd_list.keys(), key=len)

    for command in sorted(cmd_list):
        prefix = " "
        preferredWidth = 100
        wrapper = textwrap.TextWrapper(initial_indent=prefix,
                                    width=preferredWidth, subsequent_indent=' '*(len(longest_cmd)+2))
        print("{:<10} {:<15}".format(command, wrapper.fill(vehSenseCommands[command])))


def cmd_help(cmd):
    """
    Performs "help cmd", i.e, displays the syntax of individual command.

    Parameters
    -----------
        cmd: str
            The command to show more help information.
    """
    print()

    if cmd not in cmd_list:
        print("Unrecognized command. Enter \"help [cmd]\" for function syntax, \"help\" for list of available commands")
    else:
        print("Description:", vehSenseCommands[cmd], "\n")
        print("Usage:")
        cmd_list[cmd]("syntax")


def load_config(dir):
    """
    Load the configuration for basic setting

    Parameters
    ----------
    dir : str
        The folder that contains the config file

    Returns
    -------
    configs : dict
        Configs
    """
    config_file = os.path.join(dir, 'config.txt')

    configs = {}
    with open(config_file, 'r') as fp:
        for line in fp:
            line = line.rstrip()
            line = line.replace(" ", "")
            segs = line.split(",")
            configs[segs[0]] = segs[1]

    return configs


def main(args):
    """
    Takes the user input and invokes the appropriate method.
    """
    print("Welcome to Vehsense backend utility. Enter \"help\" for list of available commands.")

    data_path = '.data'
    if args.data_path:
        data_path = args.data_path
    configs = load_config(data_path)
    configs["data_path"] = data_path

    if debug:
        print(configs)

    while True:
        inputString = input(">>").rstrip()
        inputString = inputString.replace("=", " ")
        inputString = inputString.split()
        receivedCmd = inputString[0]
        if receivedCmd == "help" and len(inputString) == 1:
            helper()
        elif receivedCmd == "help" and len(inputString) == 2:
            cmd_help(inputString[1])
        elif receivedCmd == "exit":
            print("Exiting VehSense backend.")
            resume = False
            while True:
                try:
                    choice = input("Save config? (y/n): ").rstrip().lower()
                    if choice[0] == 'y':
                        # TODO: save config. But where to put it?
                        print(configs)
                        break
                    elif choice[0] == 'n':
                        print("quit without saving config")
                        break
                    elif choice == 'resume':
                        print('program resume')
                        resume = True
                        break
                except:
                    continue

            if not resume:
                sys.exit()

        elif receivedCmd in cmd_list:
            if len(inputString) == 1:
                cmd_help(inputString[0])
            else:
                cmd_list[receivedCmd](inputString[1:], configs)
        elif receivedCmd == 'cd':
            # TODO: do we need to reload config? DO NOT use this command for now
            if len(inputString) == 2:
                if os.path.isdir(inputString[1]):
                    configs = load_config(config_file)
                    configs['data_path'] = inputString[1]
                else:
                    print("given folder does not exist.")
            else:
                print("missing args")
        elif receivedCmd == 'dir':
            print(configs['data_path'])
        else:
            print("Unrecognized command. Enter \"help [cmd]\" for function syntax, \"help\" for list of available commands")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', help="used for CircleCI")
    parser.add_argument('-d', '--data_path', help='the default working directory while this script running')
    args = parser.parse_args()
    if args.test:
        print("test passed")
        sys.exit()
    main(args)
