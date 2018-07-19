import os
import pandas as pd
import csv

sampling_rate = '10L'
ref_file = "raw_obd.txt"

path = "<path>/vehsense-backend-data"

def process_data(path):
    acc = os.path.join(path,"acc.txt")
    obd = os.path.join(path,"obd.txt")
    raw_acc = os.path.join(path,"raw_acc.txt")
    raw_obd = os.path.join(path,"raw_obd.txt")
    ref_file = os.path.join(path,"raw_obd.txt")
    empty_ref_file_size = 360
    #TODO: Repeat the same for remaining file types      
    if(os.path.exists(acc) or os.path.exists(obd) or (os.stat(ref_file).st_size < empty_ref_file_size)):
        return
    for root, subdirs, files in os.walk(path):
            ref_DF = pd.read_csv(ref_file)
            for name in files: 
                if name.endswith("raw_acc.txt"):
                    print ("raw_acc.txt")
                    ##TOFIX: File doesn't exist error
                    acc_DF = pd.read_csv(raw_acc)
                if name.endswith("raw_obd.txt"):
                    print (ref_file)
                    obd_DF =  pd.read_csv(raw_obd)
            print (acc_DF.head(5))
            ref_variable = 'timestamp' # variable of obd file  
            start_time = int(ref_DF[ref_variable].head(1))
            end_time = int(ref_DF[ref_variable].tail(1))
            process_acc(acc_DF, start_time, end_time)
            process_obd(obd_DF, start_time, end_time)

def process_acc(acc_DF, start_time, end_time):
        acc_DF['sys_time'] = acc_DF['sys_time'].astype('int64')
        print(acc_DF['sys_time'].dtype)
        acc_DF = acc_DF.loc[(acc_DF['sys_time'] >= start_time) & (acc_DF['sys_time'] <= end_time)]
        acc_DF['sys_time'] = acc_DF['sys_time'] - start_time
        acc_DF['sys_time'] = pd.to_datetime(acc_DF['sys_time'], unit = 'ms')
        acc_DF = acc_DF.resample(sampling_rate, on='sys_time').mean()
        acc_DF.to_csv("raw_acc.txt")
        acc_DF = pd.read_csv("raw_acc.txt")
        acc_DF = acc_DF.dropna()
        #acc_DF = acc_DF.astype('float64')
        acc_DF.head(5)
        acc_DF1 = acc_DF.dropna()
        acc_DF1 = acc_DF.drop(['abs_timestamp', 'timestamp'],axis = 1)
        acc_DF1.to_csv("acc.txt")
        
def process_obd(obd_DF, start_time, end_time):
        obd_DF['timestamp'] = obd_DF['timestamp'] - start_time
        obd_DF['timestamp'] = pd.to_datetime(obd_DF['timestamp'], unit = 'ms')
        obd_DF1 = obd_DF.dropna(thresh=1, axis='columns')
        obd_DF1['RPM'] = obd_DF['RPM'].str.strip("RPM").astype('int64')
        obd_DF1['Speed'] = obd_DF['Speed'].str.strip("km/h").astype('int64')
        obd_DF1 = obd_DF1.rename(index=str,columns = {"timestamp":"sys_time"})
        obd_DF1 = obd_DF1.resample(sampling_rate, on='sys_time').mean()
        obd_DF1 = obd_DF1.dropna()
        obd_DF1 = obd_DF1.rename(index=str,columns = {"timestamp":"sys_time"}).head(5)
        obd_DF1['RPM'] = obd_DF1['RPM'].astype('str') + 'RPM'
        obd_DF1['Speed'] = obd_DF1['Speed'].astype('str') + 'km/h'
        obd_DF1.to_csv("obd.txt")
        obd_DF1 = pd.read_csv("obd.txt")
            
def sub_dir_path (d):
    return filter(os.path.isdir,[os.path.join(d,f) for f in os.listdir(d)])
   
def process_data_main(path):
    for subdir in sub_dir_path(path):
        subdirs = sub_dir_path(subdir)
    for subdir_datewise in subdirs:
        process_data(subdir_datewise)
        
process_data_main(path)