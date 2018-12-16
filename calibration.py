"""
Get calibration parameters for given trip(s)

Tested with Python 3.x
"""

import argparse
import os

import numpy as np

import utils
import constants


def save_array_to_file(arr):
    """
    TODO: doc
    """

    # TODO: what if the file already exists? Replace or create a new file?
    pass


def get_j(trip):
    """
    TODO: doc
    """

    # TODO: get the driving straight periods
    # TODO: get the decelerate period
    j = [0.0] * 3

    return j


def remove_gravity_component(trip):
    """
    TODO: doc
    """
    pass


def get_gravity_component(trip):
    """
    TODO: doc
    """
    # either use low filter to get the constant component
    # or find the stationary periods

    # TODO: should we save the parameters to file?
    gravity_component = [0.0] * 3
    return gravity_component


def get_calibration_parameters(trip, require_obd):
    """
    TODO: doc
    """
    gravity_component = get_gravity_component(trip)  # TODO: pass around the data instead of folder?
    remove_gravity_component(trip)
    j = get_j(trip)
    i = np.cross(gravity_component, j)

    ans = i
    ans.extend(j)
    ans.extend(gravity_component)
    save_array_to_file(ans)


def calibration(data_path, require_obd):
    """
    TODO: doc
    """
    for _root, _path, _files in os.walk(data_path):
        if os.path.join(_root, constants.ACC_FILE_NAME) not in _files:
            continue
        get_calibration_parameters(_root, require_obd)


def parse_arguments():
    """
    TODO: doc
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', dest='data_path', type=str, help="The directory that contains the data")
    parser.add_argument('--obd', dest='require_obd', type=bool, default=False, help="If set to True, then folders without obd file will not be ignored")
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

    print(data_path, args.require_obd)
    return data_path, args.require_obd


if __name__ == '__main__':
    data_path, require_obd = parse_arguments()
    calibration(data_path, require_obd)
