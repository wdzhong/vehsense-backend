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
    Creates the individual paths of files and dataframes for the individual file methods to process.

    Parameters
    ----------
    path: str,
        path of individual data folder to process

    sampling_rate : str
        Default is

    rolling_window_size : int
        Default is 50.
    Returns
    -------
    True if process succeeds; False, otherwise.
    """
    ref_file = os.path.join(path, "raw_obd.txt")
    ref_DF = pd.read_csv(ref_file)

    # get the shared start time and end time
    start_time, end_time = get_start_end_time(path)

    sensor_type = ['acc', 'gyro', 'mag', 'rot', 'grav']
    sensor_prefix = 'raw_'
    for sensor in sensor_type:
        sensor_file = os.path.join(path, sensor_prefix + sensor + '.txt')
        if os.path.isfile(sensor_file):
            process_motion_sensor_data(sensor_file, ref_DF, path, start_time, end_time, sampling_rate, rolling_window_size, sensor)

    gps_file = os.path.join(path, constants.GPS_FILE_NAME)
    if os.path.isfile(gps_file):
        df = pd.read_csv(gps_file, error_bad_lines=False, engine='python', skipfooter=1)
        process_gps(df, ref_DF, path, start_time, end_time, sampling_rate, rolling_window_size)

    obd_file = os.path.join(path, constants.OBD_FILE_NAME)
    if os.path.isfile(obd_file):  # TODO: more check
        df = pd.read_csv(obd_file, error_bad_lines=False, engine='python', skipfooter=1)
        process_obd(df, ref_DF, path, start_time, end_time, sampling_rate, rolling_window_size)

    return True


def process_motion_sensor_data(sensor_file: str, ref_df, path, start_time, end_time, sampling_rate, rolling_window_size, sensor):
    """
    Process motion sensor data, and create two new files, i.e.
        '[sensor_name]_resampled.txt' and '[sensor_name]_smoothed.txt'

    Parameters
    ----------
    sensor_file : str
        The sensor file
    """
    df = pd.read_csv(sensor_file, error_bad_lines=False, engine='python', skipfooter=1)
    resampled_file = os.path.join(path, sensor + "_resampled.txt")
    df['sys_time'] = df['sys_time'].astype('int64')
    df = df.loc[(df['sys_time'] >= start_time)
                        & (df['sys_time'] <= end_time)]
    df['sys_time'] = df['sys_time'] - start_time
    df['sys_time'] = pd.to_datetime(df['sys_time'], unit='ms')
    df = df.resample(sampling_rate, on='sys_time').mean()
    df.to_csv(resampled_file)
    df = pd.read_csv(resampled_file)
    df = df.dropna()
    pattern = '%Y-%m-%d %H:%M:%S.%f'
    for i in df.index.tolist():
        a = datetime.strptime(df.loc[i, 'sys_time'], pattern)
        a = int(a.microsecond/1000)
        x = df.at[i, 'sys_time']
        df.at[i, 'sys_time'] = a + \
            (int(calendar.timegm(time.strptime(x, pattern))) * 1000)
    df.to_csv(resampled_file, index=False)

    smoothed_file = os.path.join(path, sensor + "_smoothed.txt")
    df_smoothed = df.dropna()
    df_smoothed = df_smoothed.dropna()
    df_smoothed = df.merge(ref_df, how='left')
    df_smoothed = df.interpolate(method='linear')
    df_smoothed = df.rolling(rolling_window_size, min_periods=1).mean()
    df_smoothed = df[["sys_time", "raw_x_" + sensor, "raw_y_" + sensor, "raw_z_" + sensor]]
    df_smoothed.to_csv(smoothed_file, index=False)


def process_obd(obd_DF, ref_DF, path, start_time, end_time, sampling_rate, rolling_window_size):
    """
    Processes the 'raw_obd.txt' file and creates a new file 'obd_new.txt' with processed data 

    Args:
        obd_DF: dataframe of raw_obd.txt file

        path: path of data folder to process

        start_time: start time from reference file

        end_time: end time from reference file
    """
    raw_obd_1 = os.path.join(path, "obd_resampled.txt")
    raw_obd_2 = os.path.join(path, "obd_smoothed.txt")
    obd_DF['timestamp'] = obd_DF['timestamp'] - start_time
    obd_DF['timestamp'] = pd.to_datetime(obd_DF['timestamp'], unit='ms')
    #obd_DF['timestamp'] = obd_DF['timestamp'].astype(np.int64)
    obd_DF = obd_DF.dropna(thresh=1, axis='columns')
    obd_DF['RPM'] = obd_DF['RPM'].str.strip("RPM").astype('int64')
    obd_DF['Speed'] = obd_DF['Speed'].str.strip("km/h").astype('int64')
    obd_DF = obd_DF.rename(index=str, columns={"timestamp": "sys_time"})
    obd_DF = obd_DF.resample(sampling_rate, on='sys_time').mean()
    obd_DF = obd_DF.dropna()
    # TODO: include quote in fields for to_csv
    obd_DF.to_csv(raw_obd_1)
    obd_DF1 = pd.read_csv(raw_obd_1)
    obd_DF['RPM'] = obd_DF['RPM'].astype('str') + 'RPM'
    obd_DF['Speed'] = obd_DF['Speed'].astype('str') + 'km/h'
    obd_DF.to_csv(raw_obd_1)
    pattern = '%Y-%m-%d %H:%M:%S.%f'
    for i in obd_DF1.index.tolist():
        a = datetime.strptime(obd_DF1.loc[i, 'sys_time'], pattern)
        a = int(a.microsecond/1000)
        x = obd_DF1.at[i, 'sys_time']
        obd_DF1.at[i, 'sys_time'] = a + \
            (int(calendar.timegm(time.strptime(x, pattern))) * 1000)
    obd_DF1.to_csv(raw_obd_1, index=False)
    obd_DF1 = obd_DF1.dropna()
    obd_DF1 = obd_DF1.interpolate(method='linear')
    obd_DF1 = obd_DF1.rolling(rolling_window_size, min_periods=1).mean()
    for i in obd_DF1.index.tolist():
        x = obd_DF1.at[i, 'sys_time']
        if (x % 100 >= 50):
            obd_DF1.at[i, 'sys_time'] = int(x / 100) * 100 + 100
        else:
            obd_DF1.at[i, 'sys_time'] = int(x / 100) * 100
    obd_DF1 = obd_DF1.rename(index=str, columns={"sys_time": "timestamp"})
    obd_DF1 = obd_DF1.drop_duplicates(subset=['timestamp'], keep=False)
    obd_DF1.to_csv(raw_obd_2, index=False)


def process_gps(gps_DF, ref_DF, path, start_time, end_time, sampling_rate, rolling_window_size):
    """
    Processes the 'gps.txt' file and creates a new file 'gps_new.txt' with processed data 

    Args:
        gps_DF: dataframe of gps.txt file

        ref_DF: dataframe of reference file

        path: path of data folder to process

        start_time: start time from reference file

        end_time: end time from reference file   
    """
    # Add provider column in processed file
    raw_gps_1 = os.path.join(path, "gps_resampled.txt")
    raw_gps_2 = os.path.join(path, "gps_smoothed.txt")
    gps_DF['system_time'] = gps_DF['system_time'].astype('int64')
   # print(gps_DF['system_time'].dtype)
    gps_DF = gps_DF.loc[(gps_DF['system_time'] >= start_time)
                        & (gps_DF['system_time'] <= end_time)]
    gps_DF['system_time'] = gps_DF['system_time'] - start_time
    gps_DF['system_time'] = pd.to_datetime(gps_DF['system_time'], unit='ms')
    gps_DF = gps_DF.resample(sampling_rate, on='system_time').mean()
    pattern = '%Y-%m-%d %H:%M:%S.%f'
    gps_DF.to_csv(raw_gps_1)
    gps_DF1 = pd.read_csv(raw_gps_1)
    for i in gps_DF1.index.tolist():
        a = datetime.strptime(gps_DF1.loc[i, 'system_time'], pattern)
        a = int(a.microsecond / 1000)
        x = gps_DF1.at[i, 'system_time']
        gps_DF1.at[i, 'system_time'] = a + \
            (int(calendar.timegm(time.strptime(x, pattern))) * 1000)
    gps_DF1.to_csv(raw_gps_1, index=False)
    gps_DF1 = gps_DF1.dropna()
    gps_DF1 = gps_DF1.merge(ref_DF, how='left')
    gps_DF1 = gps_DF1.interpolate(method='linear')
    gps_DF1 = gps_DF1[["system_time", "lat", "lon", "speed", "bearing"]]
    gps_DF1 = gps_DF1.rolling(rolling_window_size, min_periods=1).mean()
    gps_DF1.to_csv(raw_gps_2, index=False)


def sub_dir_path(d):
    """
    Filters directories from the argument directory and returns the list of sub-directory folders.

    Args:
        d : directory of data

    Returns:
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
