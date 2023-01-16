# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, timezone
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
import glob
import os
import codecs

JST = timezone(timedelta(hours=+9), 'JST')

RED = '\033[31m'
END = '\033[0m'

path_e4d = ""

def read_3d_val(header):
    global path_e4d
    j=0
    csvs = []
    search_path = os.path.join(path_e4d,"**" ,header)
    csvs = glob.glob(search_path)
    print(csvs)
    k=0
    for csv in csvs:
        k += 1
        try:
            with codecs.open(csv, "r", "UTF-8", "ignore") as f:
                start_ts = list(map(float, f.readline().strip("\n").split(",")))[0]
                sampling = list(map(float, f.readline().strip("\n").split(",")))[0]
                df_tmp = pd.read_table(f, delimiter=',', header=2, names = ("x","y","z"), dtype='float')
                
                sample_num = len(df_tmp)
                start_dt = datetime.fromtimestamp(start_ts)
                smp_freq = str(1000 / int(sampling))+'ms'
                print(start_dt, sample_num, sampling, smp_freq)
                df_time_tmp = pd.DataFrame(pd.date_range(start_dt, periods=sample_num, freq = smp_freq), columns=['datetime'])

            if j == 0:
                df_acc = df_tmp
                df_time = df_time_tmp
            else:
                df_acc = pd.concat([df_acc, df_tmp], ignore_index=False)
                df_time = pd.concat([df_time, df_time_tmp], ignore_index=False)
            j = j + 1

        except:
            print(RED + "READ ERROR: " + END , csv)
            ef = open('list_readerror.txt', mode='a')
            ef.write(csv + '\n')

    df_acc = df_acc.set_index(df_time['datetime'])
    print(df_acc)

    return df_acc

def read_single_val(header):
    global path_e4d
    j=0
    csvs = []
    search_path = os.path.join(path_e4d,"**" ,header)
    csvs = glob.glob(search_path)
    print(csvs)
    k=0
    for csv in csvs:
        k += 1
        try:
            with codecs.open(csv, "r", "UTF-8", "ignore") as f:
                start_ts = float(f.readline().strip("\n"))
                sampling = float(f.readline().strip("\n"))
                df_tmp = pd.DataFrame(data=f.read().splitlines(), columns=['val'], dtype='float')               
                sample_num = len(df_tmp)
                start_dt = datetime.fromtimestamp(start_ts)
                smp_freq = str(1000 / int(sampling))+'ms'
                print(start_dt, sample_num, sampling, smp_freq)
                df_time_tmp = pd.DataFrame(pd.date_range(start_dt, periods=sample_num, freq = smp_freq), columns=['datetime'])
            if j == 0:
                df = df_tmp
                df_time = df_time_tmp
            else:
                df = pd.concat([df, df_tmp], ignore_index=False)
                df_time = pd.concat([df_time, df_time_tmp], ignore_index=False)
            j = j + 1

        except:
            print(RED + "READ ERROR: " + END , csv)
            ef = open('list_readerror.txt', mode='a')
            ef.write(csv + '\n')
    df['val'] = df['val'].astype('float')
    df = df.set_index(df_time['datetime'])
    print(df)

    return df


def main_routine():
    global path_e4d

    dirlist = glob.glob("Epw*")
    dirlist += glob.glob("epw*")
    dirlist += glob.glob("EPW*")

    print(dirlist)

    for dirname in dirlist:
        path_e4d = os.path.join(dirname,'E4_direct')
        
        pngbase = dirname + "_e4d.png"
        pngfile = os.path.join(dirname, pngbase)

        if os.path.exists(path_e4d) == False:
            print(dirname, " doesn't have E4_direct directory.")
            continue
        #--------------------------------------
        #グラフを全部描き直す時はこのブロックをコメントアウト
        if os.path.exists(pngfile):
            print(pngfile, " already exists.")
            continue
        #--------------------------------------

        print("Processing ", path_e4d)

        df_acc = read_3d_val("ACC*")
        df_bvp = read_single_val("BVP*")
        df_eda = read_single_val("EDA*")
        df_hr = read_single_val("HR*")
#        df_ibi = read_single_val("IBI_*")
        df_tp = read_single_val("TEMP*")



if __name__ == "__main__": 
    main_routine() 