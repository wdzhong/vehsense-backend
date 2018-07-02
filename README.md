# vehsense-backend
Deal with data collected from vehsense app.

The program should be running like a prompt which can accept predefined commands, e.g.
- **help**: list all available commands
- **help [cmd]**: function usage
- **clean [-acc] [-gps] [-gyro] [-obd] [--all] [-f]**: move 'bad' trip (based on the input creteria) to a temporary location for manually inspection before moving to trash. Move to trash immediately if -f is used.
- **size**: overall size, and size for each user
- **clients**: list all clients' names
- **new [-t time]**: show newly added data since last time running this command or specified time point
- **backup [-d directory]**: backup data. Ask for backup location if -d is not specified, and save it for future use.
- **etc**.
