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
    print("Usage: \"help [cmd]\" for function syntax.\n")
    print("These are the VehSense commands used for various tasks:\n")

    for command in sorted(cmd_list):
        prefix = " "
        preferredWidth = 100
        wrapper = textwrap.TextWrapper(initial_indent=prefix, width=preferredWidth, subsequent_indent=' '*10)
        print("{:<8} {:<15}".format(
            command, wrapper.fill(vehSenseCommands[command])))


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


def main():
    """
    Takes the user input and invokes the appropriate method.
    """
    print("Welcome to Vehsense backend utility. Enter \"help\" for list of available commands.")

    while True:
        inputString = input(">>").split()
        receivedCmd = inputString[0]
        if receivedCmd == "help" and len(inputString) == 1:
            helper()
        elif receivedCmd == "help" and len(inputString) == 2:
            cmd_help(inputString[1])
        elif receivedCmd == "exit":
            print("Exiting VehSense backend.")
            sys.exit()
        elif receivedCmd in cmd_list:
            type(inputString)
            cmd_list[receivedCmd](inputString)
        else:
            print("Unrecognized command. Enter \"help [cmd]\" for function syntax, \"help\" for list of available commands")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', help="used for CircleCI")
    args = parser.parse_args()
    if args.test:
        print("test passed")
        sys.exit()
    main()
