import os

import utils


def convert_to_map(list_str):
    """
    Convert a list of strings (['key', 'value', 'key', 'value', ...]) into {key: value}

    Parameters
    ----------
    list_str : list, type of element is String
        list of strings in the format of ['key', 'value', 'key', 'value', ...]

    Returns
    -------
    key_value : dict
        {key: value}
    """
    key_value = {}
    for i in range(len(list_str)):
        if i % 2 != 0:
            continue
        try:
            key_value[list_str[i]] = list_str[i + 1]
        except:
            print("Invalid number of arguments, which should be even.")
    return key_value


def valid_obd_file(obd_file):
    """
    Check if the content of the given OBD file is valid, i.e. header,
    followed by lines of data.

    Parameter
    ---------
    obd_file : str
        The path of the OBD file

    Return
    ------
    True if the content of the file is value; False, otherwise.
    """
    if not os.path.isfile(obd_file):
        return False

    with open(obd_file, 'r') as fp:
        _ = fp.readline()
        lines = fp.readlines()

        try:
            line = lines[0]
            line = line.replace('"', '').rstrip().split(',')

            # assume that the first column is time or others that can be cast to float
            _ = float(line[0])
        except:
            return False

    return True


def valid_gps_file(gps_file, max_interval=None):
    """
    Check if the content of the given gps file is valid.

    Parameter
    ---------
    gps_file : str
        The path of the gps file

    max_interval : int, default=None
        The maximum average sample interval, seconds

    Return
    ------
    True if the content of the file is value; False, otherwise.
    """
    if not os.path.isfile(gps_file):
        return False

    try:
        time_speed = utils.read_csv_file(gps_file, columns=[1, 4])  # time, speed
        if len(time_speed) == 0:
            return False

        if max_interval:
            ave_time = (time_speed[-1][0] - time_speed[0][0]) / 1000.0 / len(time_speed)
            if ave_time > max_interval:
                print("average interval of GPS samples: %.2f seconds, which is too large." % ave_time)
                return False
    except:
        return False

    return True
