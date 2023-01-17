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

def read_3d_vals(header):
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
                df_tmp = pd.read_table(f, delimiter=',', header=None, names = ("x","y","z"), dtype='float')
                
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
    df_acc = df_acc.sort_index()
#    print(df_acc)
    window = int(len(df_acc) * 0.01) + 1
    print('Rollong window: ', window)
    df_acc['mean_x'] = df_acc['x'].rolling(window).mean()
    df_acc['mean_y'] = df_acc['y'].rolling(window).mean()
    df_acc['mean_z'] = df_acc['z'].rolling(window).mean()

    return df_acc

def read_single_vals(header):
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
    df = df.sort_index()
#    print(df)
    window = int(len(df) * 0.01) + 1
    print('Rollong window: ', window)
    df['mean'] = df['val'].rolling(window).mean()

    return df

def read_ibi_vals(header):
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
                start_ts = float(list(f.readline().strip("\n").split(","))[0])
                df_tmp = pd.read_table(f, delimiter=',', header=None, names = ("time","val"), dtype='float')
                
                sample_num = len(df_tmp)
                start_dt = datetime.fromtimestamp(start_ts)
                print(start_dt, sample_num)
                f_brackets = lambda x: start_dt + timedelta(seconds=x)
                df_tmp['datetime'] = df_tmp['time'].apply(f_brackets)

            if j == 0:
                df = df_tmp
            else:
                df = pd.concat([df, df_tmp], ignore_index=False)
            j = j + 1

        except:
            print(RED + "READ ERROR: " + END , csv)
            ef = open('list_readerror.txt', mode='a')
            ef.write(csv + '\n')

    df = df.set_index('datetime', drop=True)
    df = df.sort_index()
#    print(df)
    window = int(len(df) * 0.01) + 1
    print('Rollong window: ', window)
    df['mean'] = df['val'].rolling(window).mean()

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
        
        try:
            df_acc = read_3d_vals("ACC*")
            df_bvp = read_single_vals("BVP*")
            df_eda = read_single_vals("EDA*")
            df_hr = read_single_vals("HR*")
            df_tp = read_single_vals("TEMP*")
            df_ibi = read_ibi_vals("IBI*")
        except:
            print(RED + "Exception: Something bad." + END)
            continue

        print(df_acc)
        print(df_bvp)
        print(df_eda)
        print(df_hr)
        print(df_ibi)
        print(df_tp)

#--------------------Plot-----------------

        fig = plt.figure(tight_layout=True, figsize=(12,18))
        ax1 = fig.add_subplot(611, title='E4 - [ACC]', ylabel='val')
        ax2 = fig.add_subplot(612, title='E4 - [BVP]', ylabel='val')
        ax3 = fig.add_subplot(613, title='E4 - [EDA]', ylabel='val')
        ax4 = fig.add_subplot(614, title='E4 - [HR]', ylabel='val')
        ax5 = fig.add_subplot(615, title='E4 - [IBI]', ylabel='val')
        ax6 = fig.add_subplot(616, title='E4 - [TP]', ylabel='val')

# Maximum Window
        xmin = min([df_acc.index[0], df_bvp.index[0], df_eda.index[0], df_hr.index[0], df_ibi.index[0], df_tp.index[0]])
        xmax = max([df_acc.index[len(df_acc)-1], df_bvp.index[len(df_bvp)-1], df_eda.index[len(df_eda)-1], df_hr.index[len(df_hr)-1], df_ibi.index[len(df_ibi)-1], df_tp.index[len(df_tp)-1]])

        for a in [ax1,ax2, ax3, ax4, ax5, ax6]:
            a.xaxis.set_major_formatter(md.DateFormatter('%d-%b'))
            a.xaxis.set_major_locator(md.DayLocator(interval=2,tz=JST))
            a.xaxis.set_minor_locator(md.HourLocator(byhour=range(0,24,6),tz=JST))
            a.set_xlim([xmin,xmax])

        ax1.scatter(df_acc.index,df_acc['x'], s=0.5, color='lightcoral',label='X')
        ax1.scatter(df_acc.index,df_acc['y'], s=0.5, color='lightgreen',label='Y')
        ax1.scatter(df_acc.index,df_acc['z'], s=0.5, color='lightblue',label='Z')
        ax1.plot(df_acc.index,df_acc['mean_x'],color='red',label='Mean_X')
        ax1.plot(df_acc.index,df_acc['mean_y'],color='green',label='Mean_Y')
        ax1.plot(df_acc.index,df_acc['mean_z'],color='blue',label='Mean_Z')

        ax2.scatter(df_bvp.index,df_bvp['val'], s=0.5, color='gray',label='Val')
        ax2.plot(df_bvp.index,df_bvp['mean'],color='red',label='Mean')

        ax3.scatter(df_eda.index,df_eda['val'], s=0.5, color='gray',label='Val')
        ax3.plot(df_eda.index,df_eda['mean'],color='red',label='Mean')

        ax4.scatter(df_hr.index,df_hr['val'], s=0.5, color='gray',label='Val')
        ax4.plot(df_hr.index,df_hr['mean'],color='red',label='Mean')

        ax5.scatter(df_ibi.index,df_ibi['val'], s=0.5, color='gray',label='Val')
        ax5.plot(df_ibi.index,df_ibi['mean'],color='red',label='Mean')

        ax6.scatter(df_tp.index,df_tp['val'], s=0.5, color='gray',label='Val')
        ax6.plot(df_tp.index,df_tp['mean'],color='red',label='Mean')

        plt.gcf().autofmt_xdate()

        ax1.legend(loc='upper right',fontsize=10)
        ax2.legend(loc='upper right',fontsize=10)
        ax3.legend(loc='upper right',fontsize=10)
        ax4.legend(loc='upper right',fontsize=10)
        ax5.legend(loc='upper right',fontsize=10)
        ax6.legend(loc='upper right',fontsize=10)

#    パス変更 pngfile
        plt.savefig(pngfile, dpi=200, bbox_inches="tight", pad_inches=0.1)

if __name__ == "__main__": 
    main_routine() 