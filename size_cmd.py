import os

from file_process import sub_dir_path

# Parent directory of VehSense data
parent_path = os.path.dirname(os.path.realpath(__file__))
# VehSense data directory
data_path = os.path.join(parent_path, "vehsense-backend-data")

def get_size(start_path='.'):
    """
    Calculates the size of file or directory.

    Args:
        start_path (str): path of file or directory.

    Returns:
        float: size of file or directory in KB.
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size/float(1000)


def size_cmd(cmd):
    """
    Performs the operations for the size command, i.e, displays the size of each user.

    Args:
        cmd (str): path of file or directory.
    """
    if(cmd == "syntax"):
        print("size")
    elif(len(cmd) != 1):
        print("Please enter correct syntax.")
    else:
        print(cmd)
        print("Overall size: ")
        print(get_size(data_path), "KB")
        for subdir in sub_dir_path(data_path):
            print(os.path.basename(subdir))
            print("size", get_size(subdir), "KB")
