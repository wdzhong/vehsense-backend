import os
import pandas as pd
import csv
import datetime
import numpy as np 

sampling_rate = '10L'
ref_file = "raw_obd.txt"

path = "/media/anurag/UbuntuProjects/VehSense-Dev/vehsense-backend-data"

def process_data(path):
    acc = os.path.join(path,"acc.txt")
    obd = os.path.join(path,"obd.txt")
    raw_acc = os.path.join(path,"raw_acc.txt")
    raw_obd = os.path.join(path,"raw_obd.txt")
    raw_gps = os.path.join(path,"gps.txt")
    raw_grav = os.path.join(path,"raw_grav.txt")
    raw_gyro = os.path.join(path,"raw_gyro.txt")
    raw_mag = os.path.join(path,"raw_mag.txt")
    raw_rot = os.path.join(path,"raw_rot.txt")
    ref_file = os.path.join(path,"raw_obd.txt")
    empty_ref_file_size = 360
    #TODO: Repeat the same for remaining file types   os.path.exists(acc) or os.path.exists(obd) or     
    if((os.stat(ref_file).st_size < empty_ref_file_size)):
        return
    for root, subdirs, files in os.walk(path):
            ref_DF = pd.read_csv(ref_file)
            for name in files: 
                if name.endswith("raw_acc.txt"):
                    print ("raw_acc.txt")
                    ##TOFIX: File doesn't exist error
                    acc_DF = pd.read_csv(raw_acc)
                elif name.endswith("raw_obd.txt"):
                    print (ref_file)
                    obd_DF =  pd.read_csv(raw_obd)
                elif name.endswith("gps.txt"):
                    print (ref_file)
                    gps_DF =  pd.read_csv(raw_gps)
                elif name.endswith("raw_grav.txt"):
                    print (ref_file)
                    grav_DF =  pd.read_csv(raw_grav)
                elif name.endswith("raw_mag.txt"):
                    print (ref_file)
                    #mag_DF =  pd.read_csv(raw_mag)
                elif name.endswith("raw_gyro.txt"):
                    print (ref_file)
                    #gyro_DF =  pd.read_csv(raw_gyro)
                elif name.endswith("raw_rot.txt"):
                    print (ref_file)
                    #rot_DF =  pd.read_csv(raw_rot)
            print (acc_DF.head(5))
            ref_variable = 'timestamp' # variable of obd file  
            start_time = int(ref_DF[ref_variable].head(1))
            end_time = int(ref_DF[ref_variable].tail(1))
            process_acc(acc_DF, path, start_time, end_time)
            process_obd(obd_DF, path, start_time, end_time)
            process_gps(gps_DF, path, start_time, end_time)
            process_grav(grav_DF, path, start_time, end_time)
            #process_mag(mag_DF, path, start_time, end_time)

def process_acc(acc_DF, path, start_time, end_time):
        raw_acc_1 = os.path.join(path,"acc_new.txt")
        acc_DF['sys_time'] = acc_DF['sys_time'].astype('int64')
        print(acc_DF['sys_time'].dtype)
        acc_DF = acc_DF.loc[(acc_DF['sys_time'] >= start_time) & (acc_DF['sys_time'] <= end_time)]
        acc_DF['sys_time'] = acc_DF['sys_time'] - start_time
        acc_DF['sys_time'] = pd.to_datetime(acc_DF['sys_time'], unit = 'ms')
        acc_DF = acc_DF.resample(sampling_rate, on='sys_time').mean()
        #TODO: include quote in fields for to_csv
        acc_DF.to_csv(raw_acc_1)
        acc_DF = pd.read_csv(raw_acc_1)
        acc_DF = acc_DF.dropna()
        acc_DF1 = acc_DF.dropna()
        acc_DF1.to_csv(raw_acc_1,index = False)
        
def process_obd(obd_DF, path, start_time, end_time):
        epoch = datetime.datetime.utcfromtimestamp(0)
        raw_obd_1 = os.path.join(path,"obd_new.txt")
        obd_DF['timestamp'] = obd_DF['timestamp'] - start_time
        obd_DF['timestamp'] = pd.to_datetime(obd_DF['timestamp'], unit = 'ms')
        obd_DF1 = obd_DF.dropna(thresh=1, axis='columns')
        obd_DF1['RPM'] = obd_DF['RPM'].str.strip("RPM").astype('int64')
        obd_DF1['Speed'] = obd_DF['Speed'].str.strip("km/h").astype('int64')
        obd_DF1 = obd_DF1.rename(index=str,columns = {"timestamp":"sys_time"})
        obd_DF1 = obd_DF1.resample(sampling_rate, on='sys_time').mean()
        obd_DF1 = obd_DF1.dropna()
        #TODO: include quote in fields for to_csv
        obd_DF['timestamp'] = obd_DF['timestamp'].astype(np.int64)
        #time_ref = pd.DataFrame("1970-01-01 00:00:00.000").astype(np.int64)
        #obd_DF['timestamp'] = obd_DF['timestamp'] - time_ref
        #obd_DF['timestamp'] = datetime.datetime.utcfromtimestamp(obd_DF['timestamp'])        
        obd_DF1 = obd_DF1.rename(index=str,columns = {"sys_time":"timestamp"})
        obd_DF1['RPM'] = obd_DF1['RPM'].astype('str') + 'RPM'
        obd_DF1['Speed'] = obd_DF1['Speed'].astype('str') + 'km/h'
        obd_DF1.to_csv(raw_obd_1)
    
def process_gps(gps_DF, path, start_time, end_time):
        #Add provider column in processed file
        raw_gps_1 = os.path.join(path,"gps_new.txt")
        gps_DF['system_time'] = gps_DF['system_time'].astype('int64')
        print(gps_DF['system_time'].dtype)
        gps_DF = gps_DF.loc[(gps_DF['system_time'] >= start_time) & (gps_DF['system_time'] <= end_time)]
        gps_DF['system_time'] = gps_DF['system_time'] - start_time
        gps_DF['system_time'] = pd.to_datetime(gps_DF['system_time'], unit = 'ms')
        gps_DF = gps_DF.resample(sampling_rate, on='system_time').mean()
        gps_DF.to_csv(raw_gps_1)
        gps_DF = pd.read_csv(raw_gps_1)
        gps_DF = gps_DF.dropna()
        gps_DF1 = gps_DF.dropna()
        gps_DF1.to_csv(raw_gps_1, index = False)    
        
def process_grav(grav_DF, path, start_time, end_time):
        raw_grav_1 = os.path.join(path,"grav_new.txt")
        grav_DF['sys_time'] = grav_DF['sys_time'].astype('int64')
        print(grav_DF['sys_time'].dtype)
        grav_DF = grav_DF.loc[(grav_DF['sys_time'] >= start_time) & (grav_DF['sys_time'] <= end_time)]
        grav_DF['sys_time'] = grav_DF['sys_time'] - start_time
        grav_DF['sys_time'] = pd.to_datetime(grav_DF['sys_time'], unit = 'ms')
        grav_DF = grav_DF.resample(sampling_rate, on='sys_time').mean()
        grav_DF.to_csv(raw_grav_1)
        grav_DF = pd.read_csv(raw_grav_1)
        grav_DF = grav_DF.dropna()
        grav_DF1 = grav_DF.dropna()
        grav_DF1.to_csv(raw_grav_1, index = False)    

def process_mag(mag_DF, path, start_time, end_time):
        raw_mag_1 = os.path.join(path,"mag_new.txt")
        mag_DF['sys_time'] = mag_DF['sys_time'].astype('int64')
        print(mag_DF['sys_time'].dtype)
        mag_DF = mag_DF.loc[(mag_DF['sys_time'] >= start_time) & (mag_DF['sys_time'] <= end_time)]
        mag_DF['sys_time'] = mag_DF['sys_time'] - start_time
        mag_DF['sys_time'] = pd.to_datetime(mag_DF['sys_time'], unit = 'ms')
        mag_DF = mag_DF.resample(sampling_rate, on='sys_time').mean()
        mag_DF.to_csv(raw_mag_1)
        mag_DF = pd.read_csv(raw_mag_1)
        mag_DF = mag_DF.dropna()
        mag_DF1 = mag_DF.dropna()
        mag_DF1.to_csv(raw_mag_1, index = False)     
            
def sub_dir_path (d):
    return filter(os.path.isdir,[os.path.join(d,f) for f in os.listdir(d)])
   
def process_data_main(path):
    for subdir in sub_dir_path(path):
        subdirs = sub_dir_path(subdir)
    for subdir_datewise in subdirs:
        process_data(subdir_datewise)
        
process_data_main(path)