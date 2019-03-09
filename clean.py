import os
import shutil

from helper import convert_to_map

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

def valid_acc(root):
    """
    TODO:
    """
    acc_file = os.path.join(root, constants.ACC_FILE_NAME)
    if not os.path.isfile(acc_file):
        if debug:
            print("Invalid acc file %s" % acc_file)
        return False

    return True


def valid_gyro(root):
    """
    TODO:
    """
    gyro_file = os.path.join(root, constants.GYRO_FILE_NAME)
    if not os.path.isfile(gyro_file):
        if debug:
            print("Invalid gyro file %s" % gyro_file)
        return False

    return True


def valid_obd(root):
    """
    TODO:
    """
    obd_file = os.path.join(root, constants.OBD_FILE_NAME)
    if not os.path.isfile(obd_file):
        if debug:
            print("Invalid obd file %s" % obd_file)
        return False

    # TODO: more check

    return True


def valid_gps(root, gps_max_interval, min_duration):
    """
    Check the gps file is valid or not

    Parameters
    ----------
    root : str
        The folder contains the gps file.

    gps_max_interval : int
        The maximum sampling interval of a good trip.

    min_duration : int
        The minimum duration of a good trip.

    Return
    ------
    valid : bool
        True if the gps file is good. Fasle, otherwise.
    """
    gps_file = os.path.join(root, constants.GPS_FILE_NAME)
    if not os.path.isfile(gps_file):
        if debug:
            print("no gps file %s" % root)
        return False

    time_speed = read_csv_file(gps_file, columns=[1, 4])
    trip_duration = (time_speed[-1][0] - time_speed[0][0]) / 1000.0  # seconds
    ave_time = trip_duration / len(time_speed)
    if ave_time > gps_max_interval:
        if debug:
            print("Trip: %s" % root)
            print("average interval of GPS samples: %.2f seconds, which is too large." % ave_time)
        return False

    if trip_duration / 60.0 < min_duration:
        if debug:
            print("Trip: %s" % root)
            print("Trip is too short: %.2f minutes." % (trip_duration / 60.0))
        return False

    return True


def deal_bad_trip(root, force_delete, temp_folder):
    """
    Deal with bad trip, either delete it or move it to temp_folder

    root : dir
        The path of the folder

    force_delete : str, 'True' or 'False'
        If 'True', then folder will be deleted directly.

    temp_folder : str
        The path of the temp folder to host the bad folder.
    """
    if force_delete.lower() == 'true':
        shutil.rmtree(root)
        return

    # folder_name = os.path.basename(root)
    if not os.path.isdir(temp_folder):
        os.makedirs(temp_folder)
    shutil.move(root, temp_folder)
