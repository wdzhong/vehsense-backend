import os
from datetime import datetime
import time

from dateutil import tz

from file_process import sub_dir_path

# Parent directory of VehSense data
parent_path = os.path.dirname(os.path.realpath(__file__))
# VehSense data directory
data_path = os.path.join(parent_path, "vehsense-backend-data")


def new_cmd(input_string, configs=None):
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

        if len(input_string) == 1:
            my_file = open(os.path.join(parent_path, "new_time.txt"), "r")
            specified_time = my_file.read()
            my_file.close()
        elif len(input_string) != 4:
            print("Please enter correct syntax")
            return
        else:
            specified_time = input_string[2] + " " + input_string[3]
        with open(os.path.join(parent_path, "new_time.txt"), "w") as my_file:
            utc = datetime.utcnow()
            utc = str(utc).split(".")[0]
            utc = datetime.strptime(utc, '%Y-%m-%d %H:%M:%S')
            utc = utc.replace(tzinfo=from_zone)
            central = str(utc.astimezone(to_zone))
            my_file.write(central)
            my_file.close()
        try:
            epoch = float(time.mktime(time.strptime(specified_time, pattern1)))
        except:
            print("Error in parsing time. Please check syntax.")
            return
        print("Data created after " + specified_time)
        for subdir in sub_dir_path(data_path):
            subdirs = sub_dir_path(subdir)
            print(" ")
            dest1 = os.path.basename(subdir)
            print("User ", dest1)
            for subdir_datewise in subdirs:
                sub_path = os.path.join("", subdir_datewise)
                for root, subdirs, files in os.walk(sub_path):
                    for filename in files:
                        raw_file = os.path.join(subdir_datewise, filename)
                        if(os.path.getmtime(raw_file) > epoch):
                            print(raw_file)
