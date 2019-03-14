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


def process_data(path: str, sampling_rate: int, rolling_window_size: int):
    """
    Process files under given path accordingly.

    Parameters
    ----------
    path: str
        path of individual data folder to process

    sampling_rate : int
        The resample rate, whose unit is Hz.

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


def process_motion_sensor_data(sensor_file: str, path: str, start_time: int, end_time: int, sampling_rate: int, rolling_window_size: int, sensor: str):
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

    sampling_rate : int
        The resampling rate to be used for interpolation, Hz

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

    sampling_rate : int
        The resampling rate to be used for interpolation, Hz

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

def process_gps(df, path, start_time, end_time, sampling_rate, rolling_window_size):
    """
    Processes the 'gps.txt' file and create two new files, i.e.
        'gps_resampled.txt' and 'gps_smoothed.txt'

    Parameters
    ----------
    df : DataFrame
        dataframe of gps.txt file

    path : str
        The folder/dictionary of the data exists

    start_time : int
        Any data with timestamps smaller than start time will NOT be used

    end_time : int
        And data with timestamps larger than end time will NOT be used

    sampling_rate : int
        The resampling rate to be used for interpolation, Hz

    rolling_window_size : int
        The sliding window size in data smoothing
    """
    resampled_file = os.path.join(path, "resampled_gps.txt")

    system_time_header = "system_time"
    df = df.loc[df['provider'] == "gps"]
    df[system_time_header] = df[system_time_header].astype('int64')
    df = df.loc[(df[system_time_header] >= start_time)
                        & (df[system_time_header] <= end_time)]

    # https://stackoverflow.com/questions/44305794/pandas-resample-data-frame-with-fixed-number-of-rows
    num_of_resamples = (end_time - start_time) // 1000 * sampling_rate
    time_new = np.linspace(start_time, end_time, num_of_resamples)

    num_of_rows, num_of_columns = df.values.shape

    # do not have 'provider' yet
    resampled_data = np.zeros((num_of_resamples, num_of_columns - 1))

    raw_data = df.values
    time_old = raw_data[:, 1].tolist()
    for col in range(num_of_columns - 1):  # The last column is 'provider'
        col_old = raw_data[:, col].tolist()
        resampled_data[:, col] = np.interp(time_new, time_old, col_old)

    df = pd.DataFrame(resampled_data, columns=df.columns[0: -1])
    df['provider'] = 'gps'
    df.to_csv(resampled_file, index=False)

    # df[system_time_header] = pd.to_datetime(df[system_time_header], unit='ms')
    # df = df.resample(sampling_rate, on=system_time_header).mean()
    # df = df.interpolate(method='linear')  # this cannot even guarantee that different data has the same number of rows of data
    # df['provider'] = 'gps'
    # df.to_csv(resampled_file, index=False)

    smoothed_file = os.path.join(path, "smoothed_gps.txt")
    # df = df.dropna()

    df = df[df.columns[0: -1]].rolling(rolling_window_size, min_periods=1).mean()
    df['provider'] = 'gps'
    df.to_csv(smoothed_file, index=False)


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
    # 100.0 // 5 = 20.0, instead of 20
    # sampling_rate = str(int(1000 // frequency))
    # https://stackoverflow.com/questions/17001389/pandas-resample-documentation
    # http://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
    # 'L' or 'ms', stands for milliseconds
    # sampling_rate = sampling_rate + 'L'

    for root, folders, files in os.walk(data_path):
        if root == data_path:
            continue

        # TODO: skip the 'temp' folder that are created by the 'clean' command

        good = False
        for f in files:
            if 'gps' in f:
                good = True
                break
        if not good:
            continue

        # TODO: check if the folder has been preprocessed before or not

        process_data(root, int(frequency), rolling_window_size)


if __name__ == "__main__":
    root = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(root, "vehsense-backend-data")
    sampling_rate = 200
    process_data_main(path, sampling_rate)
