import os
import pandas as pd
import csv
from datetime import datetime
import numpy as np
import time
import calendar
import sys

import constants

debug = True

def get_start_end_time(folder):
    """
    Get the maximum start time and the minimum end time of all data under the given folder.

    Parameters
    ----------
    folder : str
        The path of the folder

    Returns
    -------
    start_time : int
        System timestamp. The maximum start time of all data files.

    end_time : int
        System timestamp. The minimum end time of all data files.
    """
    start = -1
    end = sys.maxsize

    sys_time = "sys_time"

    # TODO: add more sensor
    sensor_type = [constants.ACC_FILE_NAME, constants.GYRO_FILE_NAME]

    files = os.listdir(folder)
    for f in sensor_type:
        if f in files:
            raw_acc = os.path.join(folder, constants.ACC_FILE_NAME)
            df = pd.read_csv(raw_acc, error_bad_lines=False, engine='python', skipfooter=1)
            start = max(int(df[sys_time].head(1)), start)
            end = min(int(df[sys_time].tail(1)), end)

    system_time = "system_time"
    if constants.GPS_FILE_NAME in files:
        gps_file = os.path.join(folder, constants.GPS_FILE_NAME)
        df = pd.read_csv(gps_file, error_bad_lines=False, engine='python', skipfooter=1)
        start = max(int(df[system_time].head(1)), start)
        end = min(int(df[system_time].tail(1)), end)

    if debug:
        print("start and end time: %d, %d" % (start, end))

    return start, end


def process_data(path, sampling_rate, rolling_window_size):
    """
    Process files under given path accordingly.

    Parameters
    ----------
    path: str
        path of individual data folder to process

    sampling_rate : str
        Default is

    rolling_window_size : int
        Default is 50.

    Returns
    -------
    True if process succeeds; False, otherwise.
    """

    # get the shared start time and end time
    start_time, end_time = get_start_end_time(path)

    sensor_type = ['acc', 'gyro', 'mag', 'rot', 'grav']
    sensor_prefix = 'raw_'
    for sensor in sensor_type:
        sensor_file = os.path.join(path, sensor_prefix + sensor + '.txt')
        if os.path.isfile(sensor_file):
            process_motion_sensor_data(sensor_file, ref_df, path, start_time, end_time, sampling_rate, rolling_window_size, sensor)

    gps_file = os.path.join(path, constants.GPS_FILE_NAME)
    if os.path.isfile(gps_file):
        df = pd.read_csv(gps_file, error_bad_lines=False, engine='python', skipfooter=1)
        process_gps(df, path, start_time, end_time, sampling_rate, rolling_window_size)

    obd_file = os.path.join(path, constants.OBD_FILE_NAME)
    if os.path.isfile(obd_file):  # TODO: more check
        df = pd.read_csv(obd_file, error_bad_lines=False, engine='python', skipfooter=1)
        process_obd(df, path, start_time, end_time, sampling_rate, rolling_window_size)

    return True


def process_motion_sensor_data(sensor_file: str, path, start_time, end_time, sampling_rate, rolling_window_size, sensor):
    """
    Process a single motion sensor data file, and create two new files, i.e.
        '[sensor_name]_resampled.txt' and '[sensor_name]_smoothed.txt'

    Parameters
    ----------
    sensor_file : str
        The name of sensor file

    path : str
        The folder/dictionary of the data exists

    start_time : int
        Any data with timestamps smaller than start time will NOT be used

    end_time : int
        And data with timestamps larger than end time will NOT be used

    sampling_rate : str
        The resampling rate to be used for interpolation

    rolling_window_size : int
        The sliding window size in data smoothing

    sensor : str
        The name of the sensor to be delt with, i.e. ['acc', 'gyro', 'rot', 'mag', 'grav'],
        that have been used in the filename and the column name.
    """
    df = pd.read_csv(sensor_file, error_bad_lines=False, engine='python', skipfooter=1)
    resampled_file = os.path.join(path, sensor + "_resampled.txt")
    sys_time_header = 'sys_time'
    df[sys_time_header] = df[sys_time_header].astype('int64')
    df = df.loc[(df[sys_time_header] >= start_time)
                        & (df[sys_time_header] <= end_time)]
    df[sys_time_header] = df[sys_time_header] - start_time
    df[sys_time_header] = pd.to_datetime(df[sys_time_header], unit='ms')
    df = df.resample(sampling_rate, on=sys_time_header).mean()
    df.to_csv(resampled_file)

    df = pd.read_csv(resampled_file)
    df = df.dropna()
    pattern = '%Y-%m-%d %H:%M:%S.%f'
    for i in df.index.tolist():
        a = datetime.strptime(df.loc[i, sys_time_header], pattern)
        a = int(a.microsecond/1000)
        x = df.at[i, sys_time_header]
        df.at[i, sys_time_header] = a + \
            (int(calendar.timegm(time.strptime(x, pattern))) * 1000)
    df.to_csv(resampled_file, index=False)

    smoothed_file = os.path.join(path, sensor + "_smoothed.txt")
    df_smoothed = df.dropna()
    df_smoothed = df_smoothed.dropna()
    # df_smoothed = df.merge(ref_df, how='left')
    df_smoothed = df.interpolate(method='linear')
    df_smoothed = df.rolling(rolling_window_size, min_periods=1).mean()
    df_smoothed = df[["sys_time", "raw_x_" + sensor, "raw_y_" + sensor, "raw_z_" + sensor]]
    df_smoothed.to_csv(smoothed_file, index=False)


def process_obd(obd_df, path, start_time, end_time, sampling_rate, rolling_window_size):
    """
    Processes the 'raw_obd.txt' file and create two new files, i.e.
        'obd_resampled.txt' and 'obd_smoothed.txt'

    Parameters
    ----------
    obd_df : DataFrame
        dataframe of raw_obd.txt file

    path : str
        The folder/dictionary of the data exists

    start_time : int
        Any data with timestamps smaller than start time will NOT be used

    end_time : int
        And data with timestamps larger than end time will NOT be used

    sampling_rate : str
        The resampling rate to be used for interpolation

    rolling_window_size : int
        The sliding window size in data smoothing
    """
    resampled_file = os.path.join(path, "obd_resampled.txt")
    timestamp_header = 'timestamp'
    sys_time_header = 'sys_time'
    obd_df[timestamp_header] = obd_df[timestamp_header] - start_time
    obd_df[timestamp_header] = pd.to_datetime(obd_df[timestamp_header], unit='ms')
    #obd_df[timestamp_header] = obd_df[timestamp_header].astype(np.int64)
    obd_df = obd_df.dropna(thresh=1, axis='columns')
    obd_df['RPM'] = obd_df['RPM'].str.strip("RPM").astype('int64')
    obd_df['Speed'] = obd_df['Speed'].str.strip("km/h").astype('int64')
    obd_df = obd_df.rename(index=str, columns={timestamp_header: sys_time_header})
    obd_df = obd_df.resample(sampling_rate, on=sys_time_header).mean()
    obd_df = obd_df.dropna()
    # TODO: include quote in fields for to_csv
    obd_df.to_csv(resampled_file)

    obd_df1 = pd.read_csv(resampled_file)
    obd_df['RPM'] = obd_df['RPM'].astype('str') + 'RPM'
    obd_df['Speed'] = obd_df['Speed'].astype('str') + 'km/h'
    obd_df.to_csv(resampled_file)
    pattern = '%Y-%m-%d %H:%M:%S.%f'
    for i in obd_df1.index.tolist():
        a = datetime.strptime(obd_df1.loc[i, sys_time_header], pattern)
        a = int(a.microsecond/1000)
        x = obd_df1.at[i, sys_time_header]
        obd_df1.at[i, sys_time_header] = a + \
            (int(calendar.timegm(time.strptime(x, pattern))) * 1000)
    obd_df1.to_csv(resampled_file, index=False)

    smoothed_file = os.path.join(path, "obd_smoothed.txt")
    obd_df1 = obd_df1.dropna()
    obd_df1 = obd_df1.interpolate(method='linear')
    obd_df1 = obd_df1.rolling(rolling_window_size, min_periods=1).mean()
    for i in obd_df1.index.tolist():
        x = obd_df1.at[i, sys_time_header]
        if (x % 100 >= 50):
            obd_df1.at[i, sys_time_header] = int(x / 100) * 100 + 100
        else:
            obd_df1.at[i, sys_time_header] = int(x / 100) * 100
    obd_df1 = obd_df1.rename(index=str, columns={sys_time_header: timestamp_header})
    obd_df1 = obd_df1.drop_duplicates(subset=[timestamp_header], keep=False)
    obd_df1.to_csv(smoothed_file, index=False)


def process_gps(gps_df, path, start_time, end_time, sampling_rate, rolling_window_size):
    """
    Processes the 'gps.txt' file and create two new files, i.e.
        'gps_resampled.txt' and 'gps_smoothed.txt'

    Parameters
    ----------
    gps_df : DataFrame
        dataframe of gps.txt file

    path : str
        The folder/dictionary of the data exists

    start_time : int
        Any data with timestamps smaller than start time will NOT be used

    end_time : int
        And data with timestamps larger than end time will NOT be used

    sampling_rate : str
        The resampling rate to be used for interpolation

    rolling_window_size : int
        The sliding window size in data smoothing
    """
    # TODO: Add provider column in processed file
    system_time_header = "system_time"
    resampled_file = os.path.join(path, "gps_resampled.txt")
    gps_df[system_time_header] = gps_df[system_time_header].astype('int64')
    gps_df = gps_df.loc[(gps_df[system_time_header] >= start_time)
                        & (gps_df[system_time_header] <= end_time)]
    gps_df[system_time_header] = gps_df[system_time_header] - start_time
    gps_df[system_time_header] = pd.to_datetime(gps_df[system_time_header], unit='ms')
    gps_df = gps_df.resample(sampling_rate, on=system_time_header).mean()
    pattern = '%Y-%m-%d %H:%M:%S.%f'
    gps_df.to_csv(resampled_file)

    gps_df1 = pd.read_csv(resampled_file)
    for i in gps_df1.index.tolist():
        a = datetime.strptime(gps_df1.loc[i, system_time_header], pattern)
        a = int(a.microsecond / 1000)
        x = gps_df1.at[i, system_time_header]
        gps_df1.at[i, system_time_header] = a + \
            (int(calendar.timegm(time.strptime(x, pattern))) * 1000)
    gps_df1.to_csv(resampled_file, index=False)

    smoothed_file = os.path.join(path, "gps_smoothed.txt")
    gps_df1 = gps_df1.dropna()
    gps_df1 = gps_df1.interpolate(method='linear')
    gps_df1 = gps_df1[["system_time", "lat", "lon", "speed", "bearing"]]
    gps_df1 = gps_df1.rolling(rolling_window_size, min_periods=1).mean()
    gps_df1.to_csv(smoothed_file, index=False)


def sub_dir_path(d):
    """
    Return the list of sub-directory folders of the given folder.

    Parameters
    ----------
    d : str
        The directory of data

    Returns
    -------
    List of sub-directories in the given directory.
    """
    return filter(os.path.isdir, [os.path.join(d, f) for f in os.listdir(d)])


def process_data_main(data_path, frequency, rolling_window_size=100):
    """
    Parses the directory in the provided path and processes the individual sub-directories.

    Parameters
    -----------
    data_path : str
        path of data folder to process

    frequency : int/float
        resampling frequency
    """
    sampling_rate = str(1000.0 / frequency)
    sampling_rate = sampling_rate + 'L'

    for root, folders, files in os.walk(data_path):
        if root == data_path:
            continue

        good = False
        for f in files:
            if 'gps' in f:
                good = True
                break
        if not good:
            continue

        # TODO: check if the folder has been preprocessed before or not

        process_data(root, sampling_rate, rolling_window_size)


if __name__ == "__main__":
    root = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(root, "vehsense-backend-data")
    sampling_rate = 200
    process_data_main(path, sampling_rate)
