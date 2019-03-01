"""
Utils
"""

import os
import datetime as dt
import csv
import bisect

import pickle as pk

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import constants
from constants import DATA_ATTRIBUTES


def is_float(target):
    try:
        _ = float(target)
    except ValueError:
        return False
    else:
        return True


def is_int(target):
    """
    """
    try:
        a = float(target)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


def read_csv_file(filename, columns=None, with_header=True):
    """
    Read a csv file

    Parameters:
    -----------
    filename : str
        The path of the file to be read

    columns : list, type of element should be 'int' or 'str'. Column name is case insensitive.
        The indices of columns or names of columns to be returned.
        Default is None, which means to return all columns

    with_header : boolean
        Indicate if the file has header or not. Default is 'True'.
    """
    data_type = filename.split(os.sep)[-1]
    is_gps = False
    if data_type.startswith('gps'):
        is_gps = True

    with open(filename, 'r') as f:
        if with_header:
            header = f.readline()
            header = header.replace('"', '').strip()
            col_names = header.split(',')
            col_names = [name.lower() for name in col_names]

            # print(col_names)

        # TODO: check if it is empty file

        result = []

        num_columns = None  # the number of columns in the file
        selected_cols = []  # the index of 'needed' columns
        for line in f:
            line = line.replace('"', '').strip()
            elements = line.split(',')

            if not num_columns:
                num_columns = len(elements)

                if columns:
                    if type(columns[0]) is int:
                        selected_cols = columns
                    elif type(columns[0]) is str:
                        selected_cols = [col_names.index(col.lower()) for col in columns]
                else:
                    # return all columns if parameter 'columns' is not given
                    # use num_columns instead of len(col_names), since the length of headers might be larger, e.g. raw_obd
                    selected_cols = [i for i in range(num_columns)]

            elif num_columns != len(elements):  # means the last line is incomplete
                break

            # ignore 'network' obtained gps
            if is_gps and elements[-1] == 'network':
                continue

            cur_row = []
            for col_index in selected_cols:
                value = elements[col_index]

                # need to convert from string to the right type
                if '.' in value:
                    value = float(value)
                elif is_int(value):
                    value = int(value)

                cur_row.append(value)

            result.append(cur_row)

        return np.array(result)  # to keep consistant with pandas.read_csv


def read_raw_obd(filename, columns=None):
    """
    TODO: handle cases when the last line is incomplete
    """
    if not columns:
        columns = ['timestamp', 'Speed']
    return pd.read_csv(filename, sep=",", usecols=columns, error_bad_lines=False, engine="python", skipfooter=1).values


def read_gps(filename, columns=None, ignore_network=True):
    """
    Read gps data from given file.

    Parameters
    ----------
    ignore_network : boolean, default=True
        Ignore the lines obtained via network
    """

    return read_csv_file(filename, columns=columns, with_header=True)
    # the last line might be INCOMPLETE, so that we use engine="python" here and raise warning message
    # instead of throwing error
    # return pd.read_csv(filename, usecols=columns, error_bad_lines=False, engine="python").values


def read_raw_acc(filename, columns=None):
    """
    Read acc data.
    """
    # the last line might be incomplete.
    print(filename)
    # data = pd.read_csv(filename, sep=",", usecols=columns, error_bad_lines=False, engine="python")
    # TODO: columns
    # skip the header, since header in some files are not perfectly matching the content
    # e.g. forester_weida/35823905098470/VehSenseData2018_03_20_19_56_59/raw_acc.txt
    # but this should not happen for data collected afterward
    data = pd.read_csv(filename, sep=",", usecols=[1, 3, 4, 5], skiprows=[0], header=None, error_bad_lines=False, engine="python", skipfooter=1)
    # time_stamps = data[['sys_time']].values
    # raw_acc = data[['raw_x_acc', 'raw_y_acc', 'raw_z_acc']].values

    return data.values  # time_stamps, raw_acc


def read_raw_gyro(filename, columns=None):
    """
    Read the raw gyroscope file.
    """
    # columns = ["sys_time", "raw_x_gyro", "raw_y_gyro", "raw_z_gyro"]
    data = pd.read_csv(filename, sep=",", usecols=[1, 3, 4, 5], skiprows=[0], header=None, error_bad_lines=False, engine="python")
    return data.values


def read_calibration_para(filename):
    """
    """
    return pd.read_csv(filename, sep=',', header=None).values.reshape(3, 3)


def read_pothole_truth(filename, delimiter=","):
    """
    Read the ground truth for potholes

    Parameters
    ----------
    filename : str
        The full path of the file that contains the ground truth

    delimiter : str, default=","
        The delimiter that is used to seperate each element in each row

    Returns
    --------
    truth : dict{othole_label: (depth, length)}
    """
    truth = {}
    fp = open(filename, 'r')
    for line in fp.readline():
        segments = line.strip().split(delimiter)
        pothole = int(segments[0])
        depth = float(segments[1])
        length = float(segments[2])
        truth[pothole] = (depth, length)

    return truth


def obd_file_with_valid_speed(obd_file):
    """
    Check if the given obd file has valid speed column. The file
    might be empty. The speed column might be empty.
    """
    if not file_populated(obd_file):
        return False

    time_speed = read_raw_obd(obd_file)
    if not time_speed[0][1].strip():
        return False

    return True


def get_speed(folder, sys_time):
    """
    Get the speed (km/h) at the given time point from OBD file or gps file under the specified folder.

    Parameters
    ----------
    folder: str
        The directory that contains the obd or gps files.

    sys_time: datetime object, or int/str
        The sys_time to query for speed

    Returns
    -------
    speed: float, unit km/h
        Return -1.0 if no speed can be retrieved.
    """
    if type(sys_time) is int or type(sys_time) is str:
        sys_time = timestamp_2_datetime(sys_time)

    obd_file = os.path.join(folder, constants.OBD_FILE_NAME)

    speed = None
    if obd_file_with_valid_speed(obd_file):
        speed = get_speed_obd(obd_file, sys_time)
    if speed and speed != -1.0:
        return speed

    print("No speed from obd. Try to get from gps...", end=' ')
    gps_file = os.path.join(folder, constants.GPS_FILE_NAME)
    if os.path.isfile(gps_file):
        speed = get_speed_gps(gps_file, sys_time)
    if speed and speed != -1.0:
        print('got it, %f km/h' % speed)
        return speed

    print("NO speed from gps ==> can not get speed for path %s" % folder)
    return -1.0


def get_speed_gps(gps_file, sys_time):
    """
    Get speed from the gps_file at the given sys_time

    Parameters
    ----------
    gps_file : str
        The full path of gps file to read speed data from

    sys_time : datetime object
    """
    # TODO: get the average speed in a small window? e.g. end = sys_time + datetime.timedelta(seconds=1)
    delta = dt.timedelta(seconds=1)
    return get_average_speed_gps(gps_file, sys_time - delta, sys_time - delta)


def get_average_speed_gps(gps_file, start, end):
    time_speed = read_gps(gps_file, columns=[1, 4])  # unit of gps speed is m/s
    time_speed = [(timestamp_2_datetime(int(ts[0])), float(ts[1]) * 3.6) \
                  for ts in time_speed]
    ave_speed = average_speed(time_speed, start, end)
    return ave_speed


def get_speed_obd(obd_file, start):
    """
    Returns
    -------
    Return -1.0 if no valid speed
    """
    delta = dt.timedelta(seconds=1)
    return get_average_speed_obd(obd_file, start, start)


def get_average_speed_obd(obd_file, start, end):
    """
    Returns
    -------
    Return -1.0 if no valid speed
    """
    time_speed = read_raw_obd(obd_file)
    # TODO: no need to convert all data. only need to convert the data within the required time range.
    try:
        time_speed = [(timestamp_2_datetime(ts[0]), float(str(ts[1]).split('km/h')[0])) \
                  for ts in time_speed if str(ts[1]).strip()]  # there might be some missing values
    except:
        print("exception in trying to get speed data from OBD file.")
        return -1

    ave_speed = average_speed(time_speed, start, end)
    return ave_speed


def average_speed(time_speed, start_time, end_time):
    """
    Calculate average speed within the given period.

    Parameters
    ----------
    time_speed: list[(datetime obj, speed)]
        Type of speed is float

    start_time: datetime object

    end_time: datetime object

    Returns
    -------
    Average speed between the start_time and end_time
    """
    time = [ts[0] for ts in time_speed]
    speed = [ts[1] for ts in time_speed]
    start_index = look_for_time_position(start_time, time)
    end_index = look_for_time_position(end_time, time)
    if start_index == -1 or end_index == -1:
        return -1.0
    return np.mean(speed[start_index: end_index + 1])


def look_for_time_position(target, source, begin_pos=0):
    """
    Given a time stamp, find its position in time series.
    If target does NOT exist in source, then return the value of the smallest time point
    that is larger than the given target.

    Parameters
    -------------
    target : DateTime obj
        A datetime obj to look for

    source : list, type=DateTime
        A list of DateTime objects to search from

    begin_pos : int, default=0
        The start position to search. Default to search from the beginning.

    Returns
    ---------------
    position : int
        The location
    """
    # TODO: make use of the unused parameter - begin_pos
    for i, t in enumerate(source[begin_pos:]):
        if t >= target:
            ans = i + begin_pos
            # return ans

    insert_index = bisect.bisect(source, target, lo=begin_pos)
    if insert_index >= len(source):
        # print("Error (look_for_time_position): the time is out of scope.")
        return -1
    return insert_index

    """
    # TODO: use binary search to speed up
    for i, t in enumerate(source):
        if t >= target:
            return i
    print("Error (look_for_time_position): the time is out of scope.")
    return -1
    """


def moving_average(data, windows_size):
    """
    Calculate the moving average of the given data. The row number of the return is
    (windows_size - 1) less than the input data.

    Parameters:
    -------------
    data : 2-D array
        N*M

    windows_size : int
        the size of the moving window

    Returns:
    --------------
    2-D array. The moving average
    """

    df = pd.DataFrame(data)
    mov_ave = df.rolling(window=windows_size).mean()
    return mov_ave.drop(mov_ave.index[: windows_size - 1]).values


def moving_average_same_size(data, windows_size):
    """
    Calculate the moving average of the given data. The row number of the return is
    the same as the input.
    :param data: 2-D array
    :param windows_size: int
    :return: 2-D array
    """
    result = []

    if len(data) < windows_size:
        print("error: size of data is too small")
        return result

    for i in range(windows_size):
        result.append(np.average(data[: i + 1], axis=0))
    pre_sum = np.sum(data[:windows_size, :], axis=0)
    for i in range(windows_size, len(data)):
        pre_sum -= data[i - windows_size, :]
        pre_sum += data[i, :]
        result.append(pre_sum / windows_size)

    return np.array(result)


def timestamp_2_datetime(timestamp):
    """
    Convert time stamp to datetime.

    Parameters
    --------------
    timestamp : int/float/string
        Number of seconds passed since 01/01/1970

    Returns
    --------------
    A datetime object
    """
    result = None
    try:
        result = dt.datetime.fromtimestamp(int(timestamp) / 1e3) #TODO: depending on the input, 1e3 might not need
        return result
    except:
        print(timestamp)
        exit


def append_timedate_column(raw_data, output_file, system_time_column=0):
    """
    Append a datetime column to existing data, and save the new data to the given file.

    Parameters:
    -----------
    raw_data : 2-D array
        The matrix of original data

    output_file : str
        The name of the output file to save the new data

    system_time_column : int, default=0
        The column number of system time to be transferred

    Returns:
    --------
    new_data with datetime column added
    """
    # TODO: the given column number might be invalid
    dt_column = []
    for d in raw_data:
        _dt = timestamp_2_datetime(d[system_time_column])
        dt_column.append(_dt.strftime("%Y-%m-%d-%H-%M-%S-%f"))
    dt_column = np.reshape(dt_column, (-1, 1))
    new_data = np.append(raw_data, dt_column, axis=1)

    with open(output_file, "w+", newline='') as o_f:
        wr = csv.writer(o_f)
        wr.writerows(new_data)

    return new_data


def get_files_with_given_name(root, filename, include_empty=True):
    """
    Get all files (full path) under root, with the same given name

    Parameters:
    -----------
    root : str
        The root directory to search

    filename : str
        The name of files to look for

    Returns:
    --------
    list of filenames (full paths)
    """
    all_files = []
    for _root, _, files in os.walk(root):
        for f in files:
            if f == filename:
                _path = os.path.join(_root, f)
                all_files.append(_path)
                break
    return all_files


def get_files_matching(root, prefix, extension):
    """
    Get the path of all files that match the given conditions.

    Parameters:
    -----------
    root : str
        The root directory to search in

    prefix : str
        The prefix of the target files

    extension : str
        The extension of the target files

    Returns:
    --------
    all_files : list[str]
        The list of paths of all found files
    """
    all_files = []
    for _root, _, files in os.walk(root):
        for f in files:
            if f.startswith(prefix) and f.endswith(extension):
                abs_path = os.path.join(_root, f)
                all_files.append(abs_path)
    return all_files


def get_default_data_path():
    """
    """
    return os.path.join(os.getcwd(), 'data')


def get_default_result_path():
    """
    """
    path = os.path.join(os.getcwd(), 'result')
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def is_empty_file(filepath):
    """
    Check if the given file is empty or not.

    Parameters:
    -----------
    filepath : str
        The full path of the file to be checked.

    Returns:
    ------
    result : boolean
        True if the file is empty. False, otherwise.
    """
    # TODO: what if the file does not exist at all
    return os.stat(filepath).st_size == 0


def remove_given_files(files_to_delete, filename, confirm=True):
    """
    Remove (Delete) all given files.

    Parameter:
    ----------
    files_to_delete: list
        A list of files (including full path) to be deleted.

    filename: string
        The name of file that will be deleted

    confirm: boolean, default=True
        If set to be True, then user confirmation is needed before delete.
    """
    if not files_to_delete or len(files_to_delete) == 0:
        print("nothing to delete")
        return

    delete = True  # will delete or not

    if confirm:
        while True:
            user_input = input("Are you sure you want to delete ALL %d %s files (yes/no)? " % (len(files_to_delete), filename)) \
                        .rstrip().lower()
            if user_input == 'yes':
                break
            elif user_input.startswith('n'):
                delete = False
                print("do nothing")
                break
    if delete:
        for f in files_to_delete:
            os.remove(f)


def remove_files(root, filename, confirm=True):
    """
    Remove all files wiht given name under a directory (and all its sub-folders)
    """
    files_to_delete = get_files_with_given_name(root, filename)
    remove_given_files(files_to_delete, filename, confirm=confirm)


def remove_files_matching(root, prefix, extension):
    """
    Remove all files with both matching prefix and extension
    """
    files_to_delete = get_files_matching(root, prefix, extension)
    remove_given_files(files_to_delete, prefix + '*' + extension)


def warning(msg):
    """
    """
    print("***************")
    print("Warning: " + msg)
    print("***************")


def plot_acc(time_range, acc, vertical=None, title="acc along z", show_now=True):
    """
    Plot one acc line
    """
    plt.figure()
    line_, = plt.plot(time_range, acc, '-*b', label='z')
    mean, = plt.plot(time_range, [np.mean(acc)] * len(time_range), '--g', label='mean')
    threshold, = plt.plot(time_range, [np.mean(acc) - 4.0 * np.var(acc)] * len(time_range),
                            '--r', label='threshold')
    if vertical:
        for z in vertical:
            plt.axvline(x=z, marker='o', color='c')

    plt.title(title)
    plt.legend(handles=[line_, mean, threshold])

    if show_now:
        plt.show()


def plot_(x, y, label='y', vertical=None, title="title", show_now=True):
    """
    Plot 2D.

    Parameters
    ----------
    x:

    y:

    label:

    vertical: list of integers within the range of x

    title:

    show_now:
    """
    plt.figure()
    line_, = plt.plot(x, y, '-*b', label=label)
    if vertical:
        for z in vertical:
            plt.axvline(x=z, marker='o', color='c')

    plt.title(title)
    plt.legend(handles=[line_])

    if show_now:
        plt.show()


def RMS_z(z, time, normalized=False, show_now=False):
    """
    Calculate the Root Mean Square of accelerometer of Z axis only. And plot the result.
    TODO: the interval of the calculation should be determined by speed, instead of number of samples.

    Parameters
    -----------
    z : array
        The data

    time : array, type=Datatime
        Time stamp

    normalized : boolean, default=False
        The mean of z is around 0

    show_now : boolean, default=False
        Display the figure immediately if set to be True
    """
    print("RMS")
    start_time = dt.datetime.now()
    speed = 50.  # km/h  # TODO: get the average speed of the trip??
    # need to be careful not to set it too small. How to handle the case when there is no data within certain windos
    segment_length = 2.0  # meter
    sampling_rate = 200.0  # Hz # TODO: calculate from the data, since the sampling rate could be changed
    # the number of samples for calculating the RMS
    window_size = int(segment_length / ((speed * 1000. / 3600.) / sampling_rate))
    if not normalized:
        z = z - constants.GRAVITY_OF_EARTH  # TODO: adjust the value

    # TODO: how to deal with the last window? Just ignore for now
    print("windows size: %d" % window_size)
    N = len(z) // window_size  # TODO: take the extra data into consideration?
    print("number of windows: %d" % N)

    result = []

    # cut the trip into a bunch of window-length segments, without overlapping
    # TODO: is it reasonable to use overlapping?
    for i in range(N):
        samples = z[i * window_size : (i + 1) * window_size]
        rms = np.sqrt(np.mean(samples ** 2))
        result.append(rms)

    """
    z_square = z ** 2
    for i in range(len(z)):
    # TODO: remove the redundant computation. The square of the same points has been calcualted for many times. 
        samples = z_square[max(0, i - (window_size - 1) // 2) : min(len(z), i + (window_size - 1) // 2)]
        rms = np.sqrt(np.mean(samples))
        result.append(rms)
    """

    end_time = dt.datetime.now()
    time_elapse = (end_time - start_time).total_seconds()
    print("time used " + str(time_elapse))

    plt.figure()
    # time_line = self.acc_data[:, 0][:len(result)]
    # TODO: use the actually time as X
    # time_line = time[0::window_size][0:N]
    time_line = time[window_size // 2 : : window_size][0:N]
    plt.plot(time_line, result, 'b*-', time, z)
    plt.title("RMS" + ", segment length = " + str(segment_length))
    plt.draw()

    if show_now:
        plt.show()


def file_populated(filename, with_header=True):
    """
    Check if the given file has been populated, i.e., if there are contents other than header

    Parameters
    ----------
    filename: str
        The path for the file to check

    with_header: boolean, default=True
        True if the file has header; Otherwise, False.
    Returns
    -------
    False if the file does not exist, or has no content except for header if there is; Otherwise, True.
    """
    if not os.path.isfile(filename):
        return False

    with open(filename, 'r') as fp:
        lines = fp.readlines()
        if with_header:
            return len(lines) > 1  # TODO: remove the empty line while counting
        else:
            return len(lines) > 0


def events_count(root):
    """
    Calculate how many events have been identified.
    """
    pass


def calculate_calibration_para(acc, gyro, obd, output_file):
    """
    Calculate the calibration parameter from acc data

    Parameter:
        acc : 2D array
    """
    # TODO
    pass


def save_array_to_csv(csv_file, data, header=None):
    """
    Save the given numpy data into the given csv file.

    Parameters
    -----------
    csv_file : str
        The abs path of the csv file to be written into

    data : 2-D numpy array
        The data

    header : list, default=None
        The header
    """
    with open(csv_file, 'w', newline='') as fp:
        wr = csv.writer(fp)
        if header:
            wr.writerow(header)
        wr.writerows(data)


def save_data_to_pickle(output_file, data):
    with open(output_file, 'wb') as fp:
        pk.dump(data, fp)


def save_data_attributes(output_file, x, y, car=None, trip=None, speed=None):
    data = {DATA_ATTRIBUTES.X: x, DATA_ATTRIBUTES.Y: y}
    if car:
        data[DATA_ATTRIBUTES.CAR] = car
    if trip:
        data[DATA_ATTRIBUTES.TRIP] = trip
    if speed:
        data[DATA_ATTRIBUTES.SPEED] = speed
    save_data_to_pickle(output_file, data)


def load_pickle_file(filename):
    with open(filename, 'rb') as fp:
        data = pk.load(fp)
    return data


def load_data_for_classify(filename):
    # TODO:
    pass


def load_data_for_profiling(filename):
    # TODO:
    pass


def _compare_speed_obd_vs_gps(folder):
    loss = 0.0
    obd_file = os.path.join(folder, constants.OBD_FILE_NAME)

    gps_file = os.path.join(folder, constants.GPS_FILE_NAME)

    time_speed = read_gps(gps_file, columns=[1, 4])  # unit of gps speed is m/s
    time_speed_gps = [(timestamp_2_datetime(int(ts[0])), float(ts[1]) * 3.6) \
                  for ts in time_speed]

    time_speed = read_raw_obd(obd_file)
    time_speed_obd = [(timestamp_2_datetime(ts[0]), float(str(ts[1]).split('km/h')[0])) \
                  for ts in time_speed]

    timer_begin = dt.datetime.now()
    for row in time_speed_obd[100:-100]:
        time = row[0]
        delta = dt.timedelta(seconds=1)
        # obd_speed = average_speed(time_speed_obd, time, time)
        obd_speed = row[1]
        gps_speed = average_speed(time_speed_gps, time - delta, time + delta)
        loss += abs(obd_speed - gps_speed)

    timer_end = dt.datetime.now()
    print(loss)
    print((timer_end - timer_begin).total_seconds())


if __name__ == '__main__':
    # filtered_acc_file = constants.FILTERED_ACC_FILE
    # remove_files(os.getcwd(), filtered_acc_file)

    gps_file = os.path.join(os.getcwd(), *['data', 'current', 'hongfei', 'VehSenseData2019_01_05_04_27_56', 'gps.txt'])
    gps_data = read_gps(gps_file, columns=[1, 4])
    print(gps_data[0])
    # print(type(gps_data[0][0]))

    root = os.path.join(os.getcwd(), *['data', 'current'])
    print(get_speed(root, 1546723722630))

    # TODO: compare the speed from GPS and OBD
    _compare_speed_obd_vs_gps(root)
