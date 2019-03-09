"""
Get calibration parameters for given trip(s)

Tested with Python 3.x
"""

import argparse
import os
import math
import sys

import numpy as np
from numpy.linalg import norm
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
import matplotlib.pyplot as plt
import bisect

import utils
import constants

debug = True


def print_floats(*floats, precision=4, description=None, delimeter=','):
    """
    Print a list of float in the format of specified precision.
    """
    if description:
        print(description)
    for num in floats[:-1]:
        print('%.*f' % (precision, num), end=delimeter)
    print('%.*f' % (precision, floats[-1]))


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


def valid_gps_file(gps_file):
    """
    Check if the content of the given gps file is valid.

    Parameter
    ---------
    gps_file : str
        The path of the gps file

    Return
    ------
    True if the content of the file is value; False, otherwise.
    """
    if not os.path.isfile(gps_file):
        return False

    try:
        time_speed = utils.read_csv_file(gps_file, columns=[1, 4])  # time, speed
        ave_time = (time_speed[-1][0] - time_speed[0][0]) / 1000.0 / len(time_speed)
        if ave_time > 5:  # TODO: might need to be adjusted
            print("average interval of GPS samples: %.2f seconds, which is too large." % ave_time)
            return False
    except:
        return False

    return True


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


def get_j(trip, acc, gravity_component, require_obd=False):
    """
    Get vector j from accelerating/decelerating in straight line.

    Parameters
    ----------
    trip : str
        The path of the folder

    acc : 2D numpy array
        [[time, x, y, z]]. After removing the gravity component.

    gravity_component : array
        The gravity components that are applied to the 3 axes.

    require_obd : boolean, default=False
        If True, then obd file is needed, which is mainly to retrieve speed.

    Returns
    -------
    j : vector
        1*3
    """
    j = [1.0] * 3

    # The reason to use deceleration is that deceleration usually happens ahead of
    # stop sign or traffic light, whereas acceleration could happen when turning
    # after stop sign, which means the deceleration is more likely to happen in
    # straight line.
    # but we still use acceleration period for now.
    # If we change to use deceleration later, we need to revert the sign
    # because deceleration aligns with the negative direction of j.

    obd_file = os.path.join(trip, constants.OBD_FILE_NAME)
    if valid_obd_file(obd_file):
        time_speed = utils.read_csv_file(obd_file, columns=[0, 2])
        for line in time_speed:
            if len(line) < 2:
                continue
            line[1] = line[1].split('km/h')[0]
    else:
        if require_obd:
            # throw error
            print("Error: valid OBD file %s is required to get calibration vector j." % obd_file)
            sys.exit()

        # Because we don't have OBD data for most of data collected from paratransit
        # or Stampede, we have to use speed from GPS, although it is not that accurate.

        gps_file = os.path.join(trip, constants.GPS_FILE_NAME)

        # TODO: GPS file might not be good
        # which should be taken care of by the clean in preprocess
        if not valid_gps_file(gps_file):
            print("Error: valid GPS file %s is required to get calibration vector j." % gps_file)
            return j

        # use the system_time instead of timestamp,
        # because timestamp sometime is not strictly increasing.
        # the data with provider 'network' has been filtered out during reading
        time_speed = utils.read_csv_file(gps_file, columns=[1, 4])  # time, speed

    # TODO: we don't need to use all data

    # we can get one point only, but it might be not accurate enough.
    # since it is moving straight, there will be only acceleration along
    # with y-axis in car's coordinate, and in phone's coordinate,
    # the value in each axis is proportional to the acceleration
    # so as their mean value in a time window, which can be easily proved
    new_time_speed = []
    for row in time_speed:
        new_row = [int(row[0]), float(row[1])]
        new_time_speed.append(new_row)
    new_time_speed = np.array(new_time_speed)
    time_speed = new_time_speed

    if debug:
        speed = [float(s) for s in time_speed[:, 1]]
        plt.plot(speed, '-*')

    # find all increasing time period
    # and pick up the longest one
    start = 0
    accelerating_periods = []
    longest_acc = 0
    longest_acc_period = []  # the line number of the start and end of the longest acc period
    min_accelerate_threshold = 2  # TODO: adjust the value. Setting too small could yield too many candidates.
    while start + 1 < len(time_speed):
        while start + 1 < len(time_speed) and time_speed[start][1] >= time_speed[start + 1][1]:
            start += 1
        while start + 1 < len(time_speed) and time_speed[start][1] <= time_speed[start + 1][1]:
            start += 1
        if start + 1 >= len(time_speed):
            break
        peak = start
        count = 0
        while peak > 0 and time_speed[peak][1] >= time_speed[peak - 1][1]:
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

    if not accelerating_periods:
        print("Error: cannot find accelerating period in calculating vector j, %s" % trip)
        sys.exit()

    acc_time = [int(t) for t in acc[:, 0]]  # just want to make sure the type

    # TODO: remove repeative calculation

    min_degree = 89.0
    max_degree = 91.0
    # find the dominate axis and its sign
    acc_sum = np.zeros(3)
    for period in accelerating_periods:
        start_index, end_index = period[0], period[1]
        start_time, end_time = time_speed[start_index][0], time_speed[end_index][0]

        acc_start_index = bisect.bisect(acc_time, start_time)
        acc_end_index = bisect.bisect(acc_time, end_time)

        for index in range(acc_start_index, acc_end_index):
            _acc = acc[index, 1:]
            _acc = norm_vector(_acc)

            angle = calculate_angle(_acc, gravity_component)
            angle_degree = angle / math.pi * 180
            if angle_degree < min_degree or angle_degree > max_degree:
                continue

            # TODO: add gyroscope check here

            acc_sum += np.abs(norm_vector(_acc))

    dominate_index = np.argmax(acc_sum)


    # get the sign of the dominate axis
    dominate_sign = 0
    for period in accelerating_periods:
        start_index, end_index = period[0], period[1]
        start_time, end_time = time_speed[start_index][0], time_speed[end_index][0]

        acc_start_index = bisect.bisect(acc_time, start_time)
        acc_end_index = bisect.bisect(acc_time, end_time)

        for index in range(acc_start_index, acc_end_index):
            _acc = acc[index, 1:]
            _acc = norm_vector(_acc)

            angle = calculate_angle(_acc, gravity_component)
            angle_degree = angle / math.pi * 180
            if angle_degree < min_degree or angle_degree > max_degree:
                continue

            # TODO: add gyroscope check here

            _acc_abs = np.abs(_acc)
            if np.argmax(_acc_abs) != dominate_index:
                continue

            if _acc[dominate_index] > 0:
                dominate_sign += 1
            else:
                dominate_sign -= 1


    # calculate the j for each of the period
    # and to see how different they are
    cloest_angle = 0
    for period in accelerating_periods:
    # TODO: maybe just calculate from the longest period
    # for period in [longest_acc_period]:
        start_index, end_index = period[0], period[1]
        start_time, end_time = time_speed[start_index][0], time_speed[end_index][0]

        acc_start_index = bisect.bisect(acc_time, start_time)
        acc_end_index = bisect.bisect(acc_time, end_time)

        # for each index, calculate the angle between acc and gravity
        # and pick up the one that is (the most) orthogonal with gravity component
        # this only works if we have the correct/right/accurate gravity component
        for index in range(acc_start_index, acc_end_index):
            _acc = acc[index, 1:]
            _acc = norm_vector(_acc)

            # use mean instead?
            # _acc = np.mean(acc[index: min(index + 1, acc_end_index), 1:], axis=0)
            angle = calculate_angle(_acc, gravity_component)

            angle_degree = angle / math.pi * 180
            if angle_degree < min_degree or angle_degree > max_degree:
                continue

            # TODO: add gyroscope check here

            _acc_abs = np.abs(_acc)
            if np.argmax(_acc_abs) != dominate_index:
                continue

            if _acc[dominate_index] * dominate_sign < 0:
                continue

            if abs(angle - math.pi / 2) < abs(cloest_angle - math.pi / 2):
                cloest_angle = angle
                j = _acc
                if debug:
                    print_floats(*norm_vector(j))
                    print('angle (degree): %f' % (angle / math.pi * 180))

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
        print("sign and index:", end='')
        print(dominate_sign, dominate_index)

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


def get_calibration_parameters(trip, require_obd, overwrite=False):
    """
    Get the calibration parameters for a single trip, and save them into a file
    under current folder.

    Parameters:
    ----------
    trip : str
        Folder path

    require_obd : boolean
        If True, then OBD file will be needed for calibration

    overwrite : boolean, default=False
        If True, overwrite the existing calibration parameter file.
        If False and the calibration parameter file already exists, then read the parameters from file and return.
    """
    if not overwrite:
        calib_file = os.path.join(trip, constants.CALIBRATION_FILE_NAME)
        if os.path.isfile(calib_file):
            if debug:
                print("%s already exists. And overwrite is set to be %s. Skip." % (calib_file, overwrite))
            with open(calib_file, 'r') as fp:
                line = fp.readline()
            parameters = line.rstrip().split(',')
            calibration_parameters = [float(p) for p in parameters]
            return calibration_parameters

    acc_file = os.path.join(trip, constants.ACC_FILE_NAME)
    acc = utils.read_csv_file(acc_file, columns=[1, 3, 4, 5])  # get numpy array

    gravity_component = get_gravity_from_acc(acc)
    acc_wt_gravity = remove_gravity_component(acc, gravity_component)
    j = get_j(trip, acc_wt_gravity, gravity_component, require_obd=require_obd)

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


def calibration(data_path: str, require_obd: bool, overwrite=False) -> None:
    """
    Get calibration parameters for all folders and sub folders under given path.

    Parameters
    ----------
    data_path: str
        The folder path

    require_obd: boolean
        If True, then OBD file is needed, and exception will be thrown out
        if OBD file does not exist.

    overwrite : boolean, default=False
        If True, then overwrite the existing calibration parameter file.
    """
    for _root, _, _files in os.walk(data_path):
        if not _files or (len(_files) == 1 and '.DS_Store' in _files):
            continue

        if constants.ACC_FILE_NAME not in _files:
            if debug:
                print(_root, end=': ')
                print('no acc')
            continue

        get_calibration_parameters(_root, require_obd, overwrite)


def parse_arguments():
    """
    TODO: doc
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_path', type=str,
                        help="The directory that contains the data")
    parser.add_argument('-obd', '--require_obd', default=False, action='store_true',
                        help="If used, then trips without obd file will throw out error")
    parser.add_argument('-ow', '--overwrite', default=False, action='store_true',
                        help='If used, then overwrite the existing calibration parameter file.')
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
        print('Overwrite: %s' % args.overwrite)
    return data_path, args.require_obd, args.overwrite


if __name__ == '__main__':
    data_path, require_obd, overwrite = parse_arguments()
    calibration(data_path, require_obd, overwrite=overwrite)
