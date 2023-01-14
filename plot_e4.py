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

path_e4 = ""

#------------ACC------------
def read_3d_val(header):
    global path_e4

    acc_csvs = []
    search_path = os.path.join(path_e4, header)
    csvs = glob.glob(search_path)

    j=0
    for csv in csvs:
        print(csv)

        try:
            with codecs.open(csv, "r", "UTF-8", "ignore") as f:
                df_tmp = pd.read_table(f, delimiter=',', header=1, names = ("datetime","x","y","z","dt2"))
            if j == 0:
                df_acc = df_tmp
            else:
                df_acc = pd.concat([df_acc, df_tmp], ignore_index=False)

            j = j + 1

        except:
            print(RED + "READ ERROR: " + END , csv)
            ef = open('list_readerror.txt', mode='a')
            ef.write(csv + '\n')

    df_acc['datetime'] = pd.to_datetime(df_acc['datetime'])
    df_acc = df_acc.set_index('datetime', drop=True)
    df_acc = df_acc.sort_index()

    window = int(len(df_acc) * 0.01) + 1
    print('Rollong window: ', window)
    df_acc['mean_x'] = df_acc['x'].rolling(window).mean()
    df_acc['mean_y'] = df_acc['y'].rolling(window).mean()
    df_acc['mean_z'] = df_acc['z'].rolling(window).mean()

    return df_acc


def read_single_val(header):
    global path_e4

    csvs = []
    search_path = os.path.join(path_e4, header)
    csvs = glob.glob(search_path)

    j = 0
    for csv in csvs:
        print(csv)
        try:
            with codecs.open(csv, "r", "UTF-8", "ignore") as f:
                df_tmp = pd.read_table(f, delimiter=',', header=1, names = ("datetime","val","dt2"))
            if j == 0:
                df = df_tmp
            else:
                df = pd.concat([df, df_tmp], ignore_index=False)

            j = j + 1

        except:
            print("READ ERROR: ", csv)
            ef = open('list_readerror.txt', mode='a')
            ef.write(csv + '\n')


    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime', drop=True)
    df = df.sort_index()

    window = int(len(df) * 0.01) + 1
    print('Rollong window: ', window)
    df['mean'] = df['val'].rolling(window).mean()
    
    return df

def main_routine():
    global path_e4

    dirlist = glob.glob("EPW*")
    dirlist += glob.glob("epw*")

    print(dirlist)

    for dirname in dirlist:
        path_e4 = os.path.join(dirname,'E4')
        if os.path.exists(path_e4) == False:
            print(dirname, "doesn't have E4 directory.")
            continue

        df_acc = read_3d_val("ACC_*")
        df_bvp = read_single_val("BVP_*")
        df_eda = read_single_val("EDA_*")
        df_hr = read_single_val("HR_*")
        df_ibi = read_single_val("IBI_*")
        df_tp = read_single_val("TEMP_*")

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
#        Minimum Window
#        xmin = max([df.index[0], df1.index[0], df2.index[0]])
#        xmax = min([df.index[len(df)-1], df1.index[len(df1)-1], df2.index[len(df2)-1]])
#        Hart Rate Window
#        xmin = df.index[0]
#        xmax = df.index[len(df)-1]

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
        pngbase = dirname + "_e4.png"
        pngfile = os.path.join(dirname, pngbase)
        plt.savefig(pngfile, dpi=200, bbox_inches="tight", pad_inches=0.1)
#        plt.savefig('e4.png', dpi=200, bbox_inches="tight", pad_inches=0.1)

if __name__ == "__main__": 
    main_routine() 