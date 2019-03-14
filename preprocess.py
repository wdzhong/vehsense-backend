import os

from helper import convert_to_map
from clean import clean_file
import file_process


debug = True


def preprocess(input_string, configs=None):
    """
    Performs the operations for the preprocess command, i.e, cleans the files in the specified directory and executes the preprocess functionality.

    Paremeters:
    -----------
    input_string (str array): options for preprocess command which are directory and frequency.
    """
    if input_string == "syntax":
        msg = """preprocess [-d directory] [-f frequency=200] [-c clean=False]

    -d : The data path.
    -f : The interpolation rate. Default is 200 Hz.
    -c : True then call 'clean()' function first. Default is 'False'.
        """
        print(msg)
    else:
        input_map = convert_to_map(input_string)
        frequency = float(input_map.get('-f', 200))
        data_path = input_map.get('-d', None)
        rolling_window_size = input_map.get('-w', 50)

        if not data_path and configs:
            data_path = configs['data_path']

        if not data_path:
            print("ERROR: preprocess(): data path is not set")
            return

        clean_flag = input_map.get('-c', "false")

        if debug:
            print("interpolation rate %f Hz" % frequency)
            print("data path: %s" % data_path)
            print("clean: %s" % clean_flag)

        # TODO: accept more flags for clean
        if clean_flag.lower() == 'true':
            clean_options = ["-d", data_path]
            clean_file(clean_options)

        file_process.process_data_main(data_path, frequency, rolling_window_size)


if __name__ == "__main__":
    preprocess(['-d', 'vehsense-backend-data', '-c', 'true'])
