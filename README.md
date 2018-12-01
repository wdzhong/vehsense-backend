# vehsense-backend

[![CircleCI](https://circleci.com/gh/jianpingbadao/vehsense-backend.svg?style=svg)](https://circleci.com/gh/jianpingbadao/vehsense-backend)

Deal with data collected from vehsense app.

The program should be running like a prompt which can accept predefined commands, e.g.

- **help**: list all available commands and their short descriptions.
- **[cmd]** or **help [cmd]**: show details of `cmd` usage
- **backup [-d directory]**: backup data. Ask for backup location if -d is not specified, and save it for future use.
- **clean \[--acc=True] \[--gps interval=3] \[--gyro=True] \[--obd=False] [-f]**: move 'bad' trip (based on the input creteria) to a temporary location for manually inspection before moving to trash. Keep the original file path (the last 3 or 4 layers of ancestral), rather than just the folder name so that we can put them back if necessary. Usage example: `clean --gps 4 -f`
  - `--acc=True`: The default value is `True`, which means that acc file needs to exist.
  - `--gps interval=3`: GPS file needs to be there, and its average sampling interval should NOT be larger than the specified threshold, who unit is seconds. Default is 3 seconds per point.
  - `--gyro=True`: The same as `--acc`.
  - `--obd=False`: By default, OBD file does NOT need to exist.
  - `-f`: Move to trash immediately if `-f` is used.
- **clients**: list all clients' names
- **exit**: terminal the program. Save current status.
- **new [-t time]**: show newly added data since last time running this command or specified `time` point
- **size**: overall size, and size for each user
- **unzip \[-f filename] \[-d directory] \[--compress-type='.zip'] \[--delete=False] \[--merge=True] \[--delete-unzip=True]**: decompress the speficied file, or compressed files under specified directory.
  - If ``--delete`` is set to be ``True``, then the original compressed file(s) will be deleted after decompression.
  - If ``--merge`` is ``True``, then files with the same prefix will be merged after decompression.
  - if ``--delete-unzip`` is ``True``, then the unziped files will be deleted after merge.
- **preprocess \[-d directory] \[-f frequency=200]**: preprocess files under the given directory. This can be called after unzip with merge. `clean` should have been called before this. Sync the start time of different type of data. Choose the latest one (may be added another couple of seconds) among all starts as the starting timestamp of the data that we are interested in. Then carry out interpolation.
  - ``-d directory`` The directory to deal with
  - ``-f frequency=200``: the frequency we want to interpolate. Default is 200Hz, i.e., 5ms
- **etc**.

Some information needs to be saved and read at the end and start of the program, respectively, e.g. the time point in command new, backup directory, etc.
