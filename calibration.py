"""
Get calibration parameters for given trip(s)

Tested with Python 3.x
"""

import argparse
import os

import numpy as np
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt

import utils
import constants

debug = True


def get_j(trip):
    """
    TODO: doc
    """

    # TODO: get the driving straight periods
    # TODO: get the decelerate period
    j = [0.0] * 3

    return j


def remove_gravity_component(acc, gravity):
    """
    Remove gravity component from the acc data

    Parameters
    ----------
    acc : numpy array
        [time, x, y, z]

    gravity : 1-D array

    """
    for line in acc:
        line[1:] -= gravity
    return acc


def get_gravity_component(trip):
    """
    Get gravity component from the accelerometer readings.
    either use low filter to get the constant component for each axis,
    or find the stationary periods and get the 3 values at the same time.

    Parameter
    ---------
    trip : str
        Folder path

    Return
    ------
    rotation matrix : 2-D array
        shape 3*3
    """
    print('get gravity component')
    # TODO: should we save the parameters to file?
    gravity_component = [0.0] * 3

    acc_file = os.path.join(trip, constants.ACC_FILE_NAME)
    acc = utils.read_csv_file(acc_file, columns=[1, 3, 4, 5])

    # TODO: detect the stand phase
    # https://medium.com/datadriveninvestor/how-to-build-exponential-smoothing-models-using-python-simple-exponential-smoothing-holt-and-da371189e1a1
    for i in range(3):
        # TODO: we don't need to use all rows to get the component
        #for num in range(100, len(acc), 100):
        acc_x = acc[:, i + 1]
        fit_x = SimpleExpSmoothing(acc_x).fit()
        fcast_x = fit_x.forecast(1)
        print(fcast_x)
        gravity_component[i] = fcast_x[0]
    # fcast_x.plot(marker='o', color='blue', legend=True)
    # fit_x.fittedvalues.plot(marker='o', color='blue')
    # plt.show()

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
    print('get gravity component')
    gravity_component = [0.0] * 3

    # https://medium.com/datadriveninvestor/how-to-build-exponential-smoothing-models-using-python-simple-exponential-smoothing-holt-and-da371189e1a1
    for i in range(3):
        # TODO: we don't need to use all rows to get the component
        top_rows = min(len(acc), 1000)
        acc_x = acc[:top_rows, i + 1]
        fit_x = SimpleExpSmoothing(acc_x).fit()
        fcast_x = fit_x.forecast(1)
        print(fcast_x)
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
    j = get_j(trip, acc_wt_gravity)

    gravity_component_norm = norm_vector(gravity_component)
    j_norm = norm_vector(j)
    i = np.cross(gravity_component_norm, j_norm)

    ans = i.tolist()
    ans.extend(j)
    ans.extend(gravity_component)
    output_file = os.path.join(trip, constants.CALIBRATION_FILE_NAME)
    # np.savetxt(output_file, ans, delimiter=',')
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
        print(_root)
        if constants.ACC_FILE_NAME not in _files:
            print('no acc')
            continue

        if not overwrite:
            calib_file = os.path.join(_root, constants.CALIBRATION_FILE_NAME)
            if os.path.isfile(calib_file):
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
