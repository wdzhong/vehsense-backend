import os

from utils import convert_to_map
from clean import clean_file

# Parent directory of VehSense data
parent_path = os.path.dirname(os.path.realpath(__file__))
# VehSense data directory
data_path = os.path.join(parent_path, "vehsense-backend-data")

def preprocess(input_string):
    """
    Performs the operations for the preprocess command, i.e, cleans the files in the specified directory and executes the preprocess functionality.

    Args:
        input_string (str array): options for preprocess command which are directory and frequency.
    """
    if(input_string == "syntax"):
        print("preprocess [-d directory] [-f frequency=200]")
    else:
        input_map = convert_to_map(input_string)
        frequency = float(input_map.get('-f', 5))
        preprocess_path = input_map.get('-d', data_path)
        input_string = "clean -d " + preprocess_path + " --all 170"
        clean_file(input_string.split(" "))
        print(frequency)
        print(preprocess_path)
        if(len(input_map) % 2 == 1):
            pass
            #print("Invalid arguments for preprocess")
            # return
        import file_process
        file_process.process_data_main(preprocess_path, frequency)
