import os
import shutil

from utils import convert_to_map

# Parent directory of VehSense data
parent_path = os.path.dirname(os.path.realpath(__file__))
# VehSense data directory
data_path = os.path.join(parent_path, "vehsense-backend-data")
# temporary folder for storing the data after clean if -f is specified
temp_path = os.path.join(parent_path, "vehsense-backend-data-temp")


def clean_file(input_string):
    """
    Performs the operations for the clean command, i.e, moves the files to a temporary folder or moves them to trash depending on the minimum size specified.

    Args:
        input_string (str array): options for clean command, along with the "clean" option.
    """
    if input_string == "syntax":
        msg = """clean [-acc min_size_of_acc] [-gps min_size_of_gps] [-gyro min_size_of_gyro]
            [-obd min_size_of_obd] [-grav min_size_of_grav] [-mag min_size_of_mag]
            [-rot min_size_of_rot] [--all min_size_of_file] [-f]"""
        print(msg)
    else:
        input_map = convert_to_map(input_string)
        if '-f' in input_map:
            move_trash = True
        else:
            move_trash = False
        data_path_new = input_map.get('-d', data_path)
        acc_validation = input_map.get('--acc', "True")
        gyro_validation = input_map.get('--gyro', "True")
        obd_validation = input_map.get('--obd', "False")
        gps_validation = input_map.get('', "False")
        clean_all(move_trash, acc_validation, gyro_validation, obd_validation, data_path_new)


def clean_all(move_trash, acc_validation, gyro_validation, obd_validation, data_path_new):
    """
    Performs the clean operations of the individual files, invoked from within the clean_file method.

    Args:
        move_trash (bool): true if the files need to move to trash.
        size (int): the threshold size of files in bytes.
    """
    for root, subdirs, files in os.walk(data_path_new):
        for subdir in subdirs:
            clean_all(move_trash, acc_validation, gyro_validation, obd_validation, os.path.join(data_path_new, subdir))
        if len(files) == 0:
            return
        raw_acc = os.path.join(root, "raw_acc.txt")
        raw_obd = os.path.join(root, "raw_obd.txt")
        raw_gyro = os.path.join(root, "raw_gyro.txt")
        if acc_validation == "True":
            if not os.path.exists(raw_acc):
                clean_directory(move_trash, root)
                continue
        if obd_validation == "True":
            if not os.path.exists(raw_obd):
                clean_directory(move_trash, root)
                continue
        if gyro_validation == "True":
            if not os.path.exists(raw_gyro):
                clean_directory(move_trash, root)


def clean_directory(move_trash, subdir):
    with open(os.path.join(parent_path, "cleaned_files.txt"), "a+") as my_file:
        my_file.write(os.path.realpath(subdir) + "\n")
        source = subdir
        for root, subdirs, files in os.walk(subdir):
            for filename in files:
                raw_file = os.path.join(subdir, filename)
                if (move_trash == True):
                    os.remove(raw_file)
                else:
                    print("Moving file ", raw_file)
                    dest1 = os.path.basename(subdir)
                    dest2 = os.path.basename(os.path.dirname(subdir))
                    dest_f1 = os.path.join(temp_path, dest2)
                    dest_f2 = os.path.join(dest_f1, dest1)
                    if not os.path.exists(dest_f2):
                        os.makedirs(dest_f2)
                    try:
                        shutil.move(source + "/" + filename, dest_f2)
                    except:
                        return
