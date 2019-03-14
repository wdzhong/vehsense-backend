"""
Store global constants for maintenance

e.g.
    filenames
    column names
"""
from enum import Enum

GRAVITY_OF_EARTH = 9.81

ALL_TRIPS = 'all_trips.csv'
ALL_TRIPS_FILES = 'all_trips_files.csv'
COLLECTED_DATA_FILE = 'data.pickle'

ACC_FILE_NAME = 'raw_acc.txt'
ACC_WITH_DATETIME = "acc_with_dt_added.csv"
GPS_FILE_NAME = 'gps.txt'
CALIBRATION_FILE_NAME = 'calibration_para.txt'
CALI_PARA_FILE = 'cali_para.txt'
OBD_FILE_NAME = 'raw_obd.txt'
GYRO_FILE_NAME = 'raw_gyro.txt'
GRAVITY_FILE_NAME = 'raw_grav.txt'
ROTATION_FILE_NAME = 'raw_rot.txt'
MAGNET_FILE_NAME = 'raw_mag.txt'

FILTERED_ACC_FILE = 'filtered_acc.pickle'

# the file that exists in each trip folder containing the pothole info along the trip
POTHOLES_IN_TRIP = 'potholes.txt'

# the file that holds info of all manually picked events during this trip
EVENT_FILE = 'events.txt'

# file that holds trip info
TRIP_DETAIL_FILE = '0_trip_detail.txt'

# the window size in calculating acc moving average
# MUST be odd
# Todo: adjust the windows size to achieve better performance
MOVING_WINDOW_SIZE = 25  # 15

POTHOLE_DURATION = 3 # unit: seconds

# windows size used in labeling pothole
WINDOWS_SIZE = 64
STEP_SIZE = 64

TYPE = {
    'POTHOLE': 0,
    'BUMP': 1,
    'STOP': 2
}

# for nn
ADJUSTED_SAMPLING_RATE = 200  # Hz
EVENT_DURATION = 0.6  # seconds
POINTS_PER_EVENT = int(ADJUSTED_SAMPLING_RATE * EVENT_DURATION)

class DATA_ATTRIBUTES(Enum):
    X = 1
    Y = 2
    CAR = 3
    TRIP = 4
    SPEED = 5

class CAR(Enum):
    FORESTER_WEIDA = 1
    COROLLA_QIULING = 2
    COROLLA_CHENGLIN = 3
    CAMRY_WENJUN = 4
    RAV4_CHUISHI = 5
    TOUAREG_ENSHU = 6
