import os
import pandas as pd

sampling_rate = '10L'
ref_file = "raw_obd.txt"

path = "<path>/vehsense-backend-data"

def process_data(path):
    acc = os.path.join(path,"acc.txt")
    obd = os.path.join(path,"obd.txt")
    raw_acc = os.path.join(path,"raw_acc.txt")
    ref_file = os.path.join(path,"raw_obd.txt")
    #TODO: Repeat the same for remaining file types      
    if(os.path.exists(acc) or os.path.exists(obd)):
        return
    for root, subdirs, files in os.walk(path):
            for name in files: 
                if name.endswith("raw_acc.txt"):
                    print ("raw_acc.txt")
                    ##TOFIX: File doesn't exist error
                    acc_DF = pd.read_csv(name)
                if name.endswith("raw_obd.txt"):
                    obd_DF =  pd.read_csv(name)
            ref_DF =  pd.read_csv(ref_file)
            ref_variable = 'timestamp' # variable of obd file        
            start_time = int(ref_DF[ref_variable].head(1))
            end_time = int(ref_DF[ref_variable].tail(1))
            acc_DF = acc_DF.loc[(acc_DF['sys_time'] >= start_time) & (acc_DF['sys_time'] <= end_time)]
            acc_DF['sys_time'] = acc_DF['sys_time'] - start_time
            obd_DF['timestamp'] = obd_DF['timestamp'] - start_time
            acc_DF['sys_time'] = pd.to_datetime(acc_DF['sys_time'], unit='ms')
            obd_DF['timestamp'] = pd.to_datetime(obd_DF['timestamp'], unit='ms')
            acc_DF = acc_DF.resample(sampling_rate, on='sys_time').mean()
            acc_DF.to_csv("acc.txt")
            acc_DF1 = pd.read_csv("acc.txt")
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
    