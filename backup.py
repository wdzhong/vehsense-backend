import sys
import os
import shutil

from file_process import sub_dir_path

# Parent directory of VehSense data
parent_path = os.path.dirname(os.path.realpath(__file__))
# VehSense data directory
data_path = os.path.join(parent_path, "vehsense-backend-data")


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
            print()
            print("Is this the correct backup location? (Enter \"Yes\"/\"No\").")
            print("Enter \"main\" to go back to main")
            print(backup_path)
            option = input(">>")
            if (option == "N" or option == "No" or option == "no" or option == "NO"):
                print("Enter the backup location")
                backup_path = input(">>")
            elif (option == "Y" or option == "Yes" or option == "yes" or option == "YES"):
                pass
            elif (option == "main"):
                return
            elif (option == "exit"):
                print("Exiting VehSense backend.")
                sys.exit()
            else:
                print("Please enter correct input.")
                backup(input_string)
                return
        elif (len(input_string) == 3):
            if(input_string[1] == "-d"):
                backup_path = input_string[2]
            else:
                print("Enter the correct option")
                input_string = ["backup"]
                backup(input_string)
                return
        else:
            print("Enter the correct options")
            input_string = ["backup"]
            backup(input_string)
            return
        print("Copying following files to backup location:")
        for subdir in sub_dir_path(data_path):
            subdirs = sub_dir_path(subdir)
            for subdir_datewise in subdirs:
                sub_path = os.path.join("", subdir_datewise)
                for root, subdirs, files in os.walk(sub_path):
                    for filename in files:
                        raw_file = os.path.join(subdir_datewise, filename)
                        print(raw_file)
                        source = subdir_datewise
                        dest1 = os.path.basename(subdir_datewise)
                        dest2 = os.path.basename(
                            os.path.dirname(subdir_datewise))
                        dest_f1 = os.path.join(backup_path, dest2)
                        dest_f2 = os.path.join(dest_f1, dest1)
                        if not os.path.exists(dest_f2):
                            os.makedirs(dest_f2)
                        shutil.copy(source+"/"+filename, dest_f2)
        print()
        print("Backup complete.")
