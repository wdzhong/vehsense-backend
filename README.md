# vehsense-backend

[![CircleCI](https://circleci.com/gh/jianpingbadao/vehsense-backend.svg?style=svg)](https://circleci.com/gh/jianpingbadao/vehsense-backend)

Deal with data collected from vehsense app.

## Requirements
- `Python 3.x`
- Packages: `numpy`

## Road Map
The program should be running like a prompt which can accept predefined commands (ordered alphabetically, except for the first two), e.g.

- [x] **help**: list all available commands and their short descriptions.
- [x] **[cmd]** or **help [cmd]**: show details of `cmd` usage
- [ ] **backup [-d directory]**: backup data. Ask for backup location if -d is not specified, and save it for future use.
- [x] **clean -d directory \[--acc=True] \[--gps interval=5] \[--gyro=True] \[--obd=False] [-f=False] [-temp path] [-len duration=10]**: move 'bad' trip (based on the input creteria) to a temporary location for manually inspection before moving to trash. Keep the original file path (the last 3 or 4 layers of ancestral), rather than just the folder name so that we can put them back if necessary. Usage example: `clean --gps 4 -f`
  - `-d directory`: The directory to start with.
  - `--acc=True`: The default value is `True`, which means that acc file needs to exist.
  - `--gps interval=5`: GPS file **must** be there, and its average sampling interval should **NOT** exceed the specified threshold, who unit is `second`. Default is `5 seconds per point`.
  - `--gyro=True`: The same as `--acc`.
  - `--obd=False`: By default, OBD file does **NOT** need to exist.
  - `-f=False`: Move to trash immediately if set to be `True`; otherwise, move to temp folder.
  - `-temp path`: The temp folder to save the 'bad' trips. If not provided, default is `temp` within the `directory`.
  - `-len duration=10`: The minimum duration of a good trip, default is `10 min`. Currently, `gps` file is used since it is the most important data source, and also is the most vulnerable one.
- [ ] **clients**: list all clients' names
- [x] **exit**: terminal the program. Save current status.
- [ ] **new [-t mm/dd/yyyy]**: show newly added data (trips) since the specified `time` point, last time running this command, or `yesterday`.
- [ ] **preprocess \[-d directory] \[-f frequency=200]**: preprocess files under the given directory. This can be called after unzip with merge. `clean` should have been called before this. Sync the start time of different type of data. Choose the latest one (may be added another couple of seconds) among all starts as the starting timestamp of the data that we are interested in. Then carry out interpolation.
  - ``-d directory`` The directory to deal with
  - ``-f frequency=200``: the frequency we want to interpolate. Default is 200Hz, i.e., 5ms
- [ ] **rm -d directory -p prefix -e extension \[-r=False]**: remove files that meet the given requirement under given directory:
    - `-d directory` The directory to start with.
    - `-p prefix` The prefix of files to be removed.
    - `-e extension` The extension of the files to be removed.
    - `-r=False` Recursive. If `True`, then remove files from sub folders as well.
- [ ] **size**: overall size, and size for each user
- [x] **unzip \[-f filename] \[-d directory] \[--compress-type='.zip'] \[--delete=False] \[--merge=True] \[--delete-unzip=True]**: decompress the speficied file, or all compressed files under specified directory and all sub folders.
  - If `--delete` is set to be `True`, then the original compressed file(s) will be deleted after decompression.
  - If `--merge` is `True`, then files with the same prefix will be merged after decompression.
  - if `--delete-unzip` is `True`, then the unzipped files will be deleted after merge.
- **etc**.

Some information needs to be saved and read at the end and start of the program, respectively, e.g. the time point in command new, backup directory, etc.
