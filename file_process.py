import os
import pandas as pd
import csv
from datetime import datetime
import numpy as np
import time
import calendar
import mmap
import re

global sampling_rate
sampling_rate = '100L'
ref_file = "raw_obd.txt"
rolling_window_size = 100
global memory_map
# Parent directory of VehSense data
parent_path = os.path.dirname(os.path.realpath(__file__))
# VehSense data directory
path = os.path.join(parent_path, "vehsense-backend-data")


def check_if_processed(path):
    print(path, "--------------------------")
    try:
        with open(os.path.join(parent_path, "preprocessed_files.txt"), "r") as my_file:
            lines = my_file.readlines()
            for line in lines:
                print(path, "--------------------------", line.trim())
                if line.trim() == path:

                    return True
    #            memory_map = mmap.mmap(my_file.fileno(), 0)
    #            match_object = re.search(path, memory_map)
    #            memory_map.close()
    except:
        return False
    return False


def process_data(path):
    """
    Creates the individual paths of files and dataframes for the individual file methods to process.

    Args:
        path: path of individual data folder to process

    """
    acc = os.path.join(path, "acc.txt")
    obd = os.path.join(path, "obd.txt")
    raw_acc = os.path.join(path, "raw_acc.txt")
    raw_obd = os.path.join(path, "raw_obd.txt")
    raw_gps = os.path.join(path, "gps.txt")
    raw_grav = os.path.join(path, "raw_grav.txt")
    raw_gyro = os.path.join(path, "raw_gyro.txt")
    raw_mag = os.path.join(path, "raw_mag.txt")
    raw_rot = os.path.join(path, "raw_rot.txt")
    ref_file = os.path.join(path, "raw_obd.txt")
    empty_ref_file_size = 360
    # os.path.exists(acc) or os.path.exists(obd)

    if(not os.path.exists(obd) or (os.stat(ref_file).st_size < empty_ref_file_size)):
        return

    files = [f for f in os.listdir(path) if os.path.isfile(f) and f != '.DS_Store']

    ref_DF = pd.read_csv(ref_file)
    for name in files:
        if name.endswith("raw_acc.txt"):
            acc_DF = pd.read_csv(raw_acc)
        elif name.endswith("raw_obd.txt"):
            obd_DF = pd.read_csv(raw_obd)
        elif name.endswith("gps.txt"):
            gps_DF = pd.read_csv(raw_gps)
        elif name.endswith("raw_grav.txt"):
            grav_DF = pd.read_csv(raw_grav)
        elif name.endswith("raw_mag.txt"):
            mag_DF = pd.read_csv(raw_mag, error_bad_lines=False, skipfooter=1)
        elif name.endswith("raw_gyro.txt"):
            gyro_DF = pd.read_csv(raw_gyro)
        elif name.endswith("raw_rot.txt"):
            rot_DF = pd.read_csv(raw_rot, error_bad_lines=False, skipfooter=1)
    ref_variable = 'timestamp'  # variable of obd file
    start_time = int(ref_DF[ref_variable].head(1))
    end_time = int(ref_DF[ref_variable].tail(1))
    process_acc(acc_DF, ref_DF, path, start_time, end_time)
    process_obd(obd_DF, ref_DF, path, start_time, end_time)
    process_gps(gps_DF, ref_DF, path, start_time, end_time)
    process_grav(grav_DF, ref_DF, path, start_time, end_time)
    process_gyro(gyro_DF, ref_DF, path, start_time, end_time)
    process_mag(mag_DF, ref_DF, path, start_time, end_time)
    process_rot(rot_DF, ref_DF, path, start_time, end_time)


def process_acc(acc_DF, ref_DF, path, start_time, end_time):
    """
    Processes the 'raw_acc.txt' file and creates a new file 'acc_new.txt' with processed data 

    Args:
        acc_DF: dataframe of raw_acc.txt file

        ref_DF: dataframe of reference file

        path: path of data folder to process

        start_time: start time from reference file

        end_time: end time from reference file

    """
    raw_acc_1 = os.path.join(path, "acc_resampled.txt")
    raw_acc_2 = os.path.join(path, "acc_smoothed.txt")
    acc_DF['sys_time'] = acc_DF['sys_time'].astype('int64')
    acc_DF = acc_DF.loc[(acc_DF['sys_time'] >= start_time)
                        & (acc_DF['sys_time'] <= end_time)]
    acc_DF['sys_time'] = acc_DF['sys_time'] - start_time
    acc_DF['sys_time'] = pd.to_datetime(acc_DF['sys_time'], unit='ms')
    acc_DF = acc_DF.resample(sampling_rate, on='sys_time').mean()
    # TODO: include quote in fields for to_csv

    acc_DF.to_csv(raw_acc_1)
    acc_DF = pd.read_csv(raw_acc_1)
    pattern = '%Y-%m-%d %H:%M:%S.%f'
    acc_DF = acc_DF[['sys_time', 'timestamp', 'abs_timestamp',
                     'raw_x_acc', 'raw_y_acc', 'raw_z_acc']]
    for i in acc_DF.index.tolist():
        x = acc_DF.at[i, 'sys_time']
        a = datetime.strptime(x, pattern)
        a = int(a.microsecond/1000)
        acc_DF.at[i, 'sys_time'] = (
            a + (int(calendar.timegm(time.strptime(x, pattern))) * 1000))
    acc_DF.to_csv(raw_acc_1, index=False)
    acc_DF = acc_DF.dropna()
    acc_DF1 = acc_DF.dropna()
    acc_DF1 = acc_DF1.merge(ref_DF, how='left')
    acc_DF1 = acc_DF1.interpolate(method='linear')
    acc_DF1 = acc_DF1.rolling(rolling_window_size, min_periods=1).mean()
    acc_DF1 = acc_DF1[['sys_time', 'abs_timestamp',
                       'raw_x_acc', 'raw_y_acc', 'raw_z_acc']]
    acc_DF1.to_csv(raw_acc_2, index=False)


def process_obd(obd_DF, ref_DF, path, start_time, end_time):
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


def process_gps(gps_DF, ref_DF, path, start_time, end_time):
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


def process_grav(grav_DF, ref_DF, path, start_time, end_time):
    """
    Processes the 'raw_grav.txt' file and creates a new file 'grav_new.txt' with processed data 

    Args:
        grav_DF: dataframe of raw_grav.txt file

        path: path of data folder to process

        start_time: start time from reference file

        end_time: end time from reference file
    """
    raw_grav_1 = os.path.join(path, "grav_resampled.txt")
    raw_grav_2 = os.path.join(path, "grav_smoothed.txt")
    grav_DF['sys_time'] = grav_DF['sys_time'].astype('int64')
    # print(grav_DF['sys_time'].dtype)
    grav_DF = grav_DF.loc[(grav_DF['sys_time'] >= start_time)
                          & (grav_DF['sys_time'] <= end_time)]
    grav_DF['sys_time'] = grav_DF['sys_time'] - start_time
    grav_DF['sys_time'] = pd.to_datetime(grav_DF['sys_time'], unit='ms')
    grav_DF = grav_DF.resample(sampling_rate, on='sys_time').mean()
    grav_DF.to_csv(raw_grav_1)
    grav_DF = pd.read_csv(raw_grav_1)
    pattern = '%Y-%m-%d %H:%M:%S.%f'
    for i in grav_DF.index.tolist():
        a = datetime.strptime(grav_DF.loc[i, 'sys_time'], pattern)
        a = int(a.microsecond/1000)
        x = grav_DF.at[i, 'sys_time']
        grav_DF.at[i, 'sys_time'] = a + \
            (int(calendar.timegm(time.strptime(x, pattern))) * 1000)
    grav_DF.to_csv(raw_grav_1, index=False)
    grav_DF = grav_DF.dropna()
    grav_DF1 = grav_DF.dropna()
    grav_DF1 = grav_DF1.merge(ref_DF, how='left')
    grav_DF1 = grav_DF1.interpolate(method='linear')
    grav_DF1 = grav_DF1.rolling(rolling_window_size, min_periods=1).mean()
    grav_DF1 = grav_DF1[["sys_time", "raw_x_grav", "raw_y_grav", "raw_z_grav"]]
    grav_DF1.to_csv(raw_grav_2, index=False)


def process_mag(mag_DF, ref_DF, path, start_time, end_time):
    """
    Processes the 'raw_mag.txt' file and creates a new file 'mag_new.txt' with processed data 

    Args:
        mag_DF: dataframe of raw_mag.txt file

        path: path of data folder to process

        start_time: start time from reference file

        end_time: end time from reference file

    """
    raw_mag_1 = os.path.join(path, "mag_resampled.txt")
    raw_mag_2 = os.path.join(path, "mag_smoothed.txt")
    mag_DF = mag_DF.loc[(mag_DF['sys_time'] >= start_time)
                        & (mag_DF['sys_time'] <= end_time)]
    mag_DF['sys_time'] = mag_DF['sys_time'] - start_time
    mag_DF['sys_time'] = pd.to_datetime(mag_DF['sys_time'], unit='ms')
    mag_DF = mag_DF.resample(sampling_rate, on='sys_time').mean()
    pattern = '%Y-%m-%d %H:%M:%S.%f'
    mag_DF.to_csv(raw_mag_1)
    mag_DF = pd.read_csv(raw_mag_1)
    for i in mag_DF.index.tolist():
        a = datetime.strptime(mag_DF.loc[i, 'sys_time'], pattern)
        a = int(a.microsecond/1000)
        x = mag_DF.at[i, 'sys_time']
        mag_DF.at[i, 'sys_time'] = a + \
            (int(calendar.timegm(time.strptime(x, pattern))) * 1000)
    mag_DF.to_csv(raw_mag_1, index=False)
    mag_DF = mag_DF.dropna()
    mag_DF1 = mag_DF.dropna()
    mag_DF1 = mag_DF1.merge(ref_DF, how='left')
    mag_DF1 = mag_DF1.interpolate(method='linear')
    mag_DF1 = mag_DF1.rolling(rolling_window_size, min_periods=1).mean()
    mag_DF1 = mag_DF1[["sys_time", "raw_x_mag", "raw_y_mag", "raw_z_mag"]]
    mag_DF1.to_csv(raw_mag_2, index=False)


def process_gyro(gyro_DF, ref_DF, path, start_time, end_time):
    """
    Processes the 'raw_gyro.txt' file and creates a new file 'gyro_new.txt' with processed data 

    Args:
        gyro_DF: dataframe of raw_gyro.txt file

        path: path of data folder to process

        start_time: start time from reference file

        end_time: end time from reference file

    """
    raw_gyro_1 = os.path.join(path, "gyro_resampled.txt")
    raw_gyro_2 = os.path.join(path, "gyro_smoothed.txt")
    gyro_DF['sys_time'] = gyro_DF['sys_time'].astype('int64')
    gyro_DF = gyro_DF.loc[(gyro_DF['sys_time'] >= start_time)
                          & (gyro_DF['sys_time'] <= end_time)]
    gyro_DF['sys_time'] = gyro_DF['sys_time'] - start_time
    gyro_DF['sys_time'] = pd.to_datetime(gyro_DF['sys_time'], unit='ms')
    gyro_DF = gyro_DF.resample(sampling_rate, on='sys_time').mean()
    gyro_DF.to_csv(raw_gyro_1)
    gyro_DF = pd.read_csv(raw_gyro_1)
    pattern = '%Y-%m-%d %H:%M:%S.%f'
    for i in gyro_DF.index.tolist():
        a = datetime.strptime(gyro_DF.loc[i, 'sys_time'], pattern)
        a = int(a.microsecond/1000)
        x = gyro_DF.at[i, 'sys_time']
        gyro_DF.at[i, 'sys_time'] = a + \
            (int(calendar.timegm(time.strptime(x, pattern))) * 1000)
    gyro_DF.to_csv(raw_gyro_1, index=False)
    gyro_DF = gyro_DF.dropna()
    gyro_DF1 = gyro_DF.dropna()
    gyro_DF1 = gyro_DF1.merge(ref_DF, how='left')
    gyro_DF1 = gyro_DF1.interpolate(method='linear')
    gyro_DF1 = gyro_DF1.rolling(rolling_window_size, min_periods=1).mean()
    gyro_DF1 = gyro_DF1[["sys_time", "raw_x_gyro", "raw_y_gyro", "raw_z_gyro"]]
    gyro_DF1.to_csv(raw_gyro_2, index=False)


def process_rot(rot_DF, ref_DF, path, start_time, end_time):
    """
    Processes the 'raw_rot.txt' file and creates a new file 'rot_new.txt' with processed data 

    Args:
        rot_DF: dataframe of raw_rot.txt file

        path: path of data folder to process

        start_time: start time from reference file

        end_time: end time from reference file

    """
    raw_rot_1 = os.path.join(path, "rot_resampled.txt")
    raw_rot_2 = os.path.join(path, "rot_smoothed.txt")
    rot_DF['sys_time'] = rot_DF['sys_time'].astype('int64')
    rot_DF = rot_DF.loc[(rot_DF['sys_time'] >= start_time)
                        & (rot_DF['sys_time'] <= end_time)]
    rot_DF['sys_time'] = rot_DF['sys_time'] - start_time
    rot_DF['sys_time'] = pd.to_datetime(rot_DF['sys_time'], unit='ms')
    rot_DF = rot_DF.resample(sampling_rate, on='sys_time').mean()
    rot_DF.to_csv(raw_rot_1)
    rot_DF = pd.read_csv(raw_rot_1)
    rot_DF = rot_DF.dropna()
    pattern = '%Y-%m-%d %H:%M:%S.%f'
    for i in rot_DF.index.tolist():
        a = datetime.strptime(rot_DF.loc[i, 'sys_time'], pattern)
        a = int(a.microsecond/1000)
        x = rot_DF.at[i, 'sys_time']
        rot_DF.at[i, 'sys_time'] = a + \
            (int(calendar.timegm(time.strptime(x, pattern))) * 1000)
    rot_DF.to_csv(raw_rot_1, index=False)
    rot_DF1 = rot_DF.dropna()
    rot_DF1 = rot_DF.merge(ref_DF, how='left')
    rot_DF1 = rot_DF.interpolate(method='linear')
    rot_DF1 = rot_DF.rolling(rolling_window_size, min_periods=1).mean()
    rot_DF1 = rot_DF[["sys_time", "raw_x_rot", "raw_y_rot", "raw_z_rot"]]
    rot_DF1.to_csv(raw_rot_2, index=False)


def sub_dir_path(d):
    """
    Filters directories from the argument directory and returns the list of sub-directory folders.

    Args:
        d : directory of data

    Returns:
        List of sub-directories in the given directory.
    """
    return filter(os.path.isdir, [os.path.join(d, f) for f in os.listdir(d)])


def process_data_main(data_path, frequency):
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

        process_data(root)


if __name__ == "__main__":
    parent_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(parent_path, "vehsense-backend-data")
    sampling_rate = 200
    process_data_main(path, sampling_rate)
