# vehsense-backend
Deal with data collected from vehsense app.

The program should be running like a prompt which can accept predefined commands, e.g.

- **help**: list all available commands and their short descriptions.
- **help [cmd]**: show details of `cmd` usage
- **backup [-d directory]**: backup data. Ask for backup location if -d is not specified, and save it for future use.
- **clean \[-acc] \[ -gps] \[-gyro] \[ -obd] \[--all] [-f]**: move 'bad' trip (based on the input creteria) to a temporary location for manually inspection before moving to trash. Move to trash immediately if `-f` is used.
- **clients**: list all clients' names
- **exit**: terminal the program. Save current status.
- **new [-t time]**: show newly added data since last time running this command or specified `time` point
- **size**: overall size, and size for each user
- **unzip** \[-f filename] \[-d directory] \[--compress-type='.zip'] \[--delete=False] \[--merge=True]: decompress the speficied file, or compressed files under specified directory. If ``--delete`` is set to be ``True``, then the original compressed file(s) will be deleted after decompression. If ``--merge`` is ``True``, then files with the same prefix will be merged after decompression.
- **etc**.

Some information needs to be saved and read at the end and start of the program, respectively, e.g. the time point in command new, backup directory, etc.
