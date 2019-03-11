import os
import shutil

from helper import convert_to_map
import constants
from utils import read_csv_file

debug = True


def clean_file(input_string, configs=None):
    """
    Performs the operations for the clean command, i.e, moves the files to a temporary folder
    or moves them to trash depending on the given and/or default criteria.

    Parameters:
    input_string : str, or list of str
        options for clean command.
    """
    if input_string == "syntax":
        msg = """clean -d directory [-acc=True] [-gps interval=5] [-gyro=True]
            [-obd=False] [-f=False] [-temp path] [-len duration=10]

        -f force_delete=False: If True, then delete bad folder directly. Otherwise, move to temp folder. Default is False.
        -gps interval=5: The maximum average sampling interval of a good GPS.
        -len min_duration=10: 
        -temp path: The
            """
        print(msg)
    else:
        options = convert_to_map(input_string)

        force_delete = options.get('-f', "False")
        top_folder = options.get('-d', None)

        if not top_folder and configs:
            top_folder = configs['data_path']

        if not top_folder:
            print("top folder is required")
            return

        temp_folder = options.get('-temp', os.path.join(top_folder, 'temp'))
        acc_need_valid = options.get('-acc', "True")
        gyro_need_valid = options.get('-gyro', "True")
        obd_need_valid = options.get('-obd', "False")
        gps_max_interval = int(options.get('-gps', 5))
        min_duration = int(options.get('-len', 10))

        if debug:
            print('force_detele, top folder, acc needed, gyro needed, obd needed, gps interval, temp folder, min duration')
            print(force_delete, top_folder, acc_need_valid, gyro_need_valid, obd_need_valid, gps_max_interval, temp_folder, min_duration)
        clean_all(force_delete, acc_need_valid, gyro_need_valid, obd_need_valid, top_folder, gps_max_interval, temp_folder, min_duration)


def clean_all(force_delete, acc_need_valid, gyro_need_valid, obd_need_valid, top_folder, gps_max_interval, temp_folder, min_duration):
    """
    Performs the clean operations of the individual files, invoked from within the clean_file method.

    Parameters
    ----------
    force_delete: str, 'True' or 'False'
        If 'True', then bad files will be deleted.

    acc_need_valid : str, 'True', or 'False'

    gyro_need_valid : str, 'True' or 'False'

    obd_need_valid : str, 'True' or 'False'

    top_folder : str

    gps_max_interval : int

    temp_folder : str

    min_duration: int

    """
    for root, _, _ in os.walk(top_folder):
        if root == top_folder:
            continue

        if root.startswith(temp_folder):
            continue

        clean_single_folder(root, force_delete, acc_need_valid, gyro_need_valid, obd_need_valid, gps_max_interval, temp_folder, min_duration)


def clean_single_folder(root, force_delete, acc_need_valid, gyro_need_valid, obd_need_valid, gps_max_interval, temp_folder, min_duration):
    """
    Valid the given folder as request
    """
    files = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f)) and f != '.DS_Store']
    if not files:
        return

    if (acc_need_valid.lower() == 'true' and not valid_acc(root)) or\
        (gyro_need_valid.lower() == 'true' and not valid_gyro(root)) or\
            (obd_need_valid.lower() == 'true' and not valid_obd(root)) or\
                (not valid_gps(root, gps_max_interval, min_duration)):
        deal_bad_trip(root, force_delete, temp_folder)


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
