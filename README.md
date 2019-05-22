# vehsense-backend

[![CircleCI](https://circleci.com/gh/jianpingbadao/vehsense-backend.svg?style=svg)](https://circleci.com/gh/jianpingbadao/vehsense-backend)

Deal with data collected from vehsense app.

## Requirements
- `Python 3.x`
- Packages: `numpy`, `pandas`, `matplotlib`, `statsmodels`

## Road Map
The program should be running like a prompt which can accept predefined commands (ordered alphabetically, except for the first two), e.g.

- [x] **help**: list all available commands and their short descriptions.
- [x] **[cmd]** or **help [cmd]**: show details of `cmd` usage
- [ ] **backup /path/to/data /path/to/backup**: backup data. The folder structure of original data needs to be kept. e.g., `/path/to/data/A/B -> /path/to/backup/data/A/B`.
  - Need to figure out how to avoid backuping the same file for multiple times
  - Eventually make this command run automatically, e.g. using [Crontab](https://www.howtogeek.com/101288/how-to-schedule-tasks-on-linux-an-introduction-to-crontab-files/).
- [x] **calibration -d directory [-obd require_obd=False] [-o overwrite=False]**: Calculate the rotation matrix for coordinates alignment for all folders in the given directory and save the matrix into `calibration_para.txt` in corresponding folder:
  - `-d directory`: The directory to start with
  - `-obd require_obd=False`: If `True`, then `obd` file is needed to calculated the parameters
  - `-o overwrite=False`: If 'True`, then existing file containing calibration parameters will be overwritten.
- [x] **clean [-d directory=data] \[-acc=True] \[-gps interval=5] \[-gyro=True] \[-obd=False] [-f=False] [-temp path=TEMP_TEMP_TEMP] [-len duration=10]**: move 'bad' trip (based on the input creteria) to a temporary location for manually inspection before moving to trash. Keep the original file path (the last 3 or 4 layers of ancestral), rather than just the folder name so that we can put them back if necessary. Usage example: `clean -gps 4 -f`
  - `-d directory`: The directory to start with.
  - `-acc=True`: The default value is `True`, which means that acc file needs to exist.
  - `-gps interval=5`: GPS file **must** be there, and its average sampling interval should **NOT** exceed the specified threshold, who unit is `second`. Default is `5 seconds per point`.
  - `-gyro=True`: The same as `--acc`.
  - `-obd=False`: By default, OBD file does **NOT** need to exist.
  - `-f=False`: Move to trash immediately if set to be `True`; otherwise, move to temp folder.
  - `-temp path=TEMP_TEMP_TEMP`: The temp folder to save the 'bad' trips. If not provided, default is `TEMP_TEMP_TEMP` within the `directory`.
  - `-len duration=10`: The minimum duration of a good trip, default is `10 min`. Currently, `gps` file is used since it is the most important data source, and also is the most vulnerable one.
- [ ] **clients**: list all clients' names
- [x] **exit**: terminal the program. Save current status.
- [ ] **new [-t mm/dd/yyyy]**: show newly added data (trips) since the specified `time` point, last time running this command, or `yesterday`.
- [x] **preprocess \[-d directory=data] \[-f frequency=200]**: preprocess files under the given directory. This may be called after `unzip` with merge. Aand `clean` should have been called as well. Sync the start timestamps of different type of data and choose the latest one (on which may add another couple of seconds) as the start point of the current data. Then carry out interpolation.
  - `-d directory` The directory to deal with. Temp folder `TEMP_TEMP_TEMP` populated from `clean` cmd will be ignored.
  - `-f frequency=200`: The frequency we want to interpolate. Default is 200Hz, i.e., 5ms
  - `-w rolling_window_size=100` : The size of sliding window in data smoothing.
  - `-c clean=False`: If `True`, then it will call `clean` first before `preprocess`.
- [x] **rm [directory=data] prefix suffix \[-f force=False]**: remove files that meet the given requirement under given directory:
    - `directory`: The directory to start with. Default is `./data`.
    - `prefix`: The prefix of files to be removed, which can be empty, i.e. `""`.
    - `suffix`: The suffix of files to be removed, which can be empty, i.e. `""`.
    - (**TODO**) `-f force=False`: If `True`, then remove files without user confirm.
- [ ] **size**: overall size, and size for each user
- [x] **unzip \[-f filename] \[-d directory=data] \[--compress-type='.zip'] \[--delete=False] \[--merge=True] \[--delete-unzip=True]**: decompress the speficied file, or all compressed files under specified directory and all sub folders.
  - If `--delete` is set to be `True`, then the original compressed file(s) will be deleted after decompression.
  - If `--merge` is `True`, then files with the same prefix will be merged after decompression.
  - if `--delete-unzip` is `True`, then the unzipped files will be deleted after merge.
- **etc**.

**TODO**: Some information needs to be saved and read at the end and start of the program, respectively, e.g. the time point in command new, backup directory, etc.


## Usage

```python
python main.py
```


# More about calibration

Implement coordinate alignment algorithm used in paper `Wang, Yan, et al. "Sensing vehicle dynamics for determining driver phone use." Proceeding of the 11th annual international conference on Mobile systems, applications, and services. ACM, 2013.`

## Road Map
- [x] Derive **k**
  - [x] Retrieve the gravity acceleration applied to 3 axes one by one through [low pass filter](https://medium.com/datadriveninvestor/how-to-build-exponential-smoothing-models-using-python-simple-exponential-smoothing-holt-and-da371189e1a1)
  - [ ] Use different number of data will yield different result. Need to figure out how to get a more reliable result.
- [x] Derive **j**
  - [x] Remove the gravity component obtained from last step
  - [x] Get all the periods of car accelerating through OBD or GPS data.
  - [x] Check the acc readings within all the selected periods, and pick up the acc reading that is mostly orthogonal to the gravity component as **j**
    - [ ] Use gyroscope to fine tune **j**, i.e. check if the vehicle is driving straight in the selected periods
- [x] Obtain **i**
  - [x] Normalize **j** and **k** to unit vectors
  - [x] **i** = **j** X **k**, where `X` is [cross product](https://en.wikipedia.org/wiki/Cross_product). If **j** and **k** are accurate, then **i** should already be normalized to be an unit vector.
  - [x] Save `[i, j, k]` to file, i.e. `calibration_para.txt`
  
## Usage
To run
```Python
python calibration.py [-d data_folder] [-obd] [-o]
```
 - `-d`, `--data_path`: the path to the data. If not provided or the provided is invalid folder, then it will try to use `./data`.
 - `-obd`, `--require_obd`: default is `False`; If used, set value to `True`. If `True`, then folers without `obd` file will throw exception.
 - `-o`, `--overwrite`: default is `False`; If used, set value to `True`. If `True`, then existing `calibration_para.txt` files will be overwritten. Otherwise, folders with `calibration_para.txt` file will be ignored.
