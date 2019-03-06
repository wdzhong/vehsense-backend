"""
Get calibration parameters for given trip(s)

Tested with Python 3.x
"""

import argparse
import os
import math

import numpy as np
from numpy.linalg import norm
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
import matplotlib.pyplot as plt
import bisect

import utils
import constants

debug = True


def calculate_angle(v1, v2):
    """
    Calculate the angle ([0, Pi]) between two vectors

    p = u * v = |u||v|cos(a)

    Parameters
    ----------
    v1 : arr
    v2 : arr

    Returns
    -------
    angle : float
        The angle ([0, Pi]) between these two given vectors
    """
    product = np.dot(v1, v2)
    cos_a = product / norm(v1) / norm(v2)
    return np.arccos(cos_a)


def get_j(trip, acc, gravity_component):
    """
    Get vector j from accelerating/decelerating in straight line.

    Parameters
    ----------
    trip : str
        The path of the folder

    acc : 2D numpy array
        [[time, x, y, z]]. After removing the gravity component.

    Returns
    -------
    j : vector
        1*3
    """
    j = [1.0] * 3
    # Since most of time, the car is driving straight, we first get the decelerate period.
    # since we don't have OBD data for most of data collected from paratransit
    # or Stampede,  use GPS approximately
    # the reason to use deceleration is that deceleration usually happens ahead of
    # stop sign or traffic light, whereas acceleration could happen when turning
    # after stop sign
    # but we can use acceleration period near the top speed
    gps_file = os.path.join(trip, constants.GPS_FILE_NAME)

    # use the system_time instead of timestamp,
    # because timestamp sometime is not strictly increasing.
    # the data with provider 'network' has been filtered out during reading
    gps = utils.read_csv_file(gps_file, columns=[1, 4])  # time, speed

    # we can get one point only, but it might be not accurate enough.
    # since it is moving straight, there will be only acceleration along
    # with y-axis in car's coordinate, and in phone's coordinate,
    # the value in each axis is proportional to the acceleration
    # so as their mean value in a time window, which can be easily proved
    new_gps = []
    for row in gps:
        new_row = [int(row[0]), float(row[1])]
        new_gps.append(new_row)
    new_gps = np.array(new_gps)
    gps = new_gps

    if debug:
        speed = [float(s) for s in gps[:, 1]]
        plt.plot(speed, '-*')

    # find all increasing time period
    # and pick up the longest one
    start = 0
    accelerating_periods = []
    longest_acc = 0
    longest_acc_period = []  # the line number of the start and end of the longest acc period
    min_accelerate_threshold = 2  # TODO: adjust the value. Setting too small could yield too many candidates.
    while start + 1 < len(gps):
        while start + 1 < len(gps) and gps[start][1] >= gps[start + 1][1]:
            start += 1
        while start + 1 < len(gps) and gps[start][1] < gps[start + 1][1]:
            start += 1
        if start + 1 >= len(gps):
            break
        peak = start
        count = 0
        while peak > 0 and gps[peak][1] > gps[peak - 1][1]:
            peak -= 1
            count += 1
        if count >= min_accelerate_threshold:
            if debug:
                plt.axvline(x=start, marker='x', color='g')
                plt.axvline(x=peak, marker='o', color='r')
            accelerating_periods.append([peak, start])
            if count > longest_acc:
                longest_acc = count
                longest_acc_period = [peak, start]
        start += 1

    # calculate the j for each of the period
    # and to see how different they are
    acc_time = [int(t) for t in acc[:, 0]]
    cloest_angle = 0
    for period in accelerating_periods:
        start_index, end_index = period[0], period[1]
        start_time, end_time = gps[start_index][0], gps[end_index][0]

        acc_start_index = bisect.bisect(acc_time, start_time)
        acc_end_index = bisect.bisect(acc_time, end_time)

        # for each index, calculate the angle between acc and gravity
        # and pick up the one that is (the most) orthogonal with gravity component
        # this only works if we have the correct/right/accurate gravity component
        for index in range(acc_start_index, acc_end_index):
            _acc = acc[index, 1:]
            angle = calculate_angle(_acc, gravity_component)

            # TODO: add gyroscope check here

            if abs(angle - math.pi / 2) < abs(cloest_angle - math.pi / 2):
                cloest_angle = angle
                j = _acc
                if debug:
                    print(j)
                    print('angle: %f' % angle)

        '''
        # assume that when the car reaches its highest speed, it goes straight
        # which might not hold for some cases
        # get the average of acc of this periods
        acc_mean = np.mean(acc[acc_end_index - 3: acc_end_index, 1:], axis=0)
        print(norm_vector(acc_mean))
        if period == longest_acc_period:
            print('from longest acc period')
            j = acc_mean
        '''

    if debug:
        plt.draw()
        plt.show()

    # TODO: get the driving straight periods.
    # via gyroscope. Find the period with the smallest variance of gyroscope?
    # gyro_file = os.path.join(trip, constants.GYRO_FILE_NAME)
    # gyro = utils.read_csv_file(gyro_file, columns=[1, 3, 4, 5])

    return j


def remove_gravity_component(acc, gravity):
    """
    Remove gravity component from the acc data

    Parameters
    ----------
    acc : numpy array
        [time, x, y, z]

    gravity : 1-D array
        gravity component along 3 axes

    Returns
    -------
    The acc that has the gravity component removed.
    """
    for line in acc:
        line[1:] -= gravity
    return acc


def get_gravity_component(trip):
    """
    Get gravity component from the accelerometer readings.
    either use low filter to get the constant component for each axis,
    or find the stationary periods and get the 3 values at the same time.

    Parameters
    ---------
    trip : str
        Folder path

    Return
    ------
    rotation matrix : 2-D array
        shape 3*3
    """
    if debug:
        print('get gravity component')
    # TODO: should we save the parameters to file?
    # so that we don't need to recalculate?
    # in the end, saving the full calibration parameter should be enough
    gravity_component = [0.0] * 3

    acc_file = os.path.join(trip, constants.ACC_FILE_NAME)
    acc = utils.read_csv_file(acc_file, columns=[1, 3, 4, 5])

    gravity_component = get_gravity_from_acc(acc)

    return gravity_component


def get_gravity_from_acc(acc):
    """
    Get gravity from acc data by using low pass filter

    Parameters
    ----------
    acc : numpy array
        [time, x, y, z]

    Returns
    --------
    gravity : 1-D array
        The gravity component in 3 axis
    """
    if debug:
        print('get gravity component')
    gravity_component = [0.0] * 3

    # use low pass filter (exponential)
    # https://developer.android.com/guide/topics/sensors/sensors_motion
    # https://medium.com/datadriveninvestor/how-to-build-exponential-smoothing-models-using-python-simple-exponential-smoothing-holt-and-da371189e1a1
    for i in range(3):
        # TODO: we don't need to use all rows to get the component
        top_rows = min(len(acc), 1000)
        acc_x = acc[:top_rows, i + 1]
        fit_x = SimpleExpSmoothing(acc_x).fit()
        fcast_x = fit_x.forecast(1)
        gravity_component[i] = fcast_x[0]

    if debug:
        print('gravity component: ', end='')
        print(gravity_component)

    return gravity_component


def norm_vector(vector):
    """
    Normalize a vector
    """
    norm = np.sqrt(np.sum(np.square(vector)))
    normed = [v / norm for v in vector]
    return normed


def get_calibration_parameters(trip, require_obd):
    """
    Get the calibration parameters for a single trip, and save them into a file
    under current folder.

    Parameters:
    ----------
    trip : str
        Folder path

    require_obd : boolean
        If True, then OBD file will be needed for calibration
    """
    acc_file = os.path.join(trip, constants.ACC_FILE_NAME)
    acc = utils.read_csv_file(acc_file, columns=[1, 3, 4, 5])  # get numpy array

    gravity_component = get_gravity_from_acc(acc)
    acc_wt_gravity = remove_gravity_component(acc, gravity_component)
    j = get_j(trip, acc_wt_gravity, gravity_component)

    gravity_component_norm = norm_vector(gravity_component)
    j_norm = norm_vector(j)
    i = np.cross(j_norm, gravity_component_norm)

    ans = i.tolist()
    ans.extend(j_norm)
    ans.extend(gravity_component_norm)
    output_file = os.path.join(trip, constants.CALIBRATION_FILE_NAME)

    with open(output_file, 'w') as fp:
        fp.write(','.join([str(a) for a in ans]))
    return ans


def calibration(data_path: str, require_obd: bool, overwrite=True) -> None:
    """
    Get calibration parameters for all folders and sub folders under given path.

    Parameters
    ----------
    data_path: str
        The folder path

    require_obd: boolean
        If True, then OBD file is needed, and exception will be thrown out
        if OBD file does not exist.

    overwrite : boolean, default=True
        If True, then overwrite the existing calibration parameter file.
    """
    for _root, _, _files in os.walk(data_path):
        if not _files:
            continue

        if constants.ACC_FILE_NAME not in _files:
            if debug:
                print(_root, end=': ')
                print('no acc')
            continue

        if not overwrite:
            calib_file = os.path.join(_root, constants.CALIBRATION_FILE_NAME)
            if os.path.isfile(calib_file):
                if debug:
                    print("%s already exists. And overwrite is set to be %s. Skip" % (calib_file, overwrite))
                continue
        get_calibration_parameters(_root, require_obd)


def parse_arguments():
    """
    TODO: doc
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', dest='data_path', type=str,
                        help="The directory that contains the data")
    parser.add_argument('--obd', dest='require_obd', type=bool, default=False,
                        help="If set to True, then folders without obd file will not be ignored")
    # TODO: add more
    args = parser.parse_args()

    if args.data_path:
        data_path = args.data_path
        if not os.path.isdir(data_path):
            data_path = os.path.join(os.getcwd(), args.data_path)
            if not os.path.isdir(data_path):
                data_path = utils.get_default_data_path()
    else:
        data_path = utils.get_default_data_path()

    if debug:
        print("Options:")
        print("data path: %s" % data_path)
        print("require OBD: %s" % args.require_obd)
    return data_path, args.require_obd


if __name__ == '__main__':
    data_path, require_obd = parse_arguments()
    calibration(data_path, require_obd)
