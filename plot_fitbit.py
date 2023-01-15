# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta, timezone
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
import glob
import os

RED = '\033[31m'
END = '\033[0m'

JST = timezone(timedelta(hours=+9), 'JST')

dirlist = glob.glob("Epw*")
dirlist += glob.glob("epw*")
dirlist += glob.glob("EPW*")

activities = ['sedentary','lightly_active','moderately_active','very_active']

print(dirlist)

def read_HeartRate(search_path):
    global dt_list

    hr_jsons = []
    hr_jsons = glob.glob(search_path)

    dt_list = []
    bpm_list = []

    for hr_json in hr_jsons:
        print(hr_json)
        f = open(hr_json ,'r')
        jsonData = json.load(f)

        for i in range(len(jsonData)):
            dt = datetime.strptime(jsonData[i]['dateTime'], '%m/%d/%y %H:%M:%S')
            bpm = float(jsonData[i]['value']['bpm'])

            dt_list.append(dt)
            bpm_list.append(bpm)

    df_dt = pd.DataFrame(data=dt_list, columns=['datetime'])
    df_bpm = pd.DataFrame(data=bpm_list, columns=['bpm'])
    df_mean = pd.DataFrame(data=df_bpm['bpm'], columns=['mean'])

    df = pd.concat([df_dt,df_bpm,df_mean], ignore_index=False, axis=1)
    df = df.set_index('datetime', drop=True)
    df = df.sort_index()

    window = int(len(df) * 0.01) + 1
    print('Rollong window: ', window)
    df['mean'] = df['bpm'].rolling(window).mean()
    print(df)

    return df

def read_Activity(search_path_base):
    global dt_list

    j=0
    middlen = '_minutes'
    activ_min_f = []
    am_list = []

    for activity in activities:
        j = j + 1
        job = activity + middlen + "*"
        search_path = os.path.join(search_path_base, job)
        activ_min_f = glob.glob(search_path)

        for activ_min in activ_min_f:
            print(activ_min)
            f = open(activ_min ,'r')
            jsonData = json.load(f)

            dt_list.clear()
            am_list.clear()

            for i in range(len(jsonData)):
                dt = datetime.strptime(jsonData[i]['dateTime'], '%m/%d/%y %H:%M:%S')
                actvmin = float(jsonData[i]['value'])

                dt_list.append(dt)
                am_list.append(actvmin)

        df_dt2 = pd.DataFrame(data=dt_list, columns=['datetime'])
        df_am = pd.DataFrame(data=am_list, columns=[activity])
        df_tmp = pd.concat([df_dt2,df_am], ignore_index=False, axis=1)

        if j == 1:
            df1 = df_tmp
        else:
            df1 = pd.merge(df1, df_tmp, on='datetime', how="left")

    df1 = df1.set_index('datetime', drop=True)
    df1 = df1.sort_index()
    print(df1)

    return df1

def conv_eov(x):

    result = x * (0.1) + 97  #formula from "fitbit forum (2020)"

    if result > 100:
        result = 100
    elif result < 0:
        result = 0
    else:
        pass

    return result


def read_SpO2(search_path):
    global dt_list

    eov_csvs = []
    eov_csvs = glob.glob(search_path)

    dt_list = []
    R_list = []
    j=0
    for eov_csv in eov_csvs:
        j = j + 1
        print(eov_csv)
        f = open(eov_csv ,'r')
        df_tmp = pd.read_csv(f, header=1, names = ("timestamp","R"))
        if j == 1:
            df2 = df_tmp
        else:
            df2 = pd.concat([df2, df_tmp], ignore_index=False)

    df2['timestamp'] = pd.to_datetime(df2['timestamp'])
    df2 = df2.set_index('timestamp', drop=True)
    df2 = df2.sort_index()

    df2['eov'] = df2['R'].apply(conv_eov)
    df2['m_eov'] = df2['eov'].rolling(100).mean()
    print(df2)

    return df2

def read_Sleep(search_path):
    keywords = ['data', 'shortData']
    dic_level_val = {'deep':0, 'light':1, 'rem':2, 'wake':3, 'asleep':0, 'restless':1, 'awake':2}
    for k in range(len(keywords)):
        dt_list = []
        level_list = []
        leval_list = []
        seconds_list = []
        type_list = []

        slp_jsons = glob.glob(search_path)

        f = open(slp_jsons[0] ,'r')
        jsonData = json.load(f)

        for i in range(len(jsonData)):
            log_type = jsonData[i]['type']
            if keywords[k] not in jsonData[i]['levels']:
                continue
#            print(jsonData[i]['levels'][keywords[k]])
            for j in range(len(jsonData[i]['levels'][keywords[k]])):
                dt = datetime.strptime(jsonData[i]['levels'][keywords[k]][j]['dateTime'], '%Y-%m-%dT%H:%M:%S.%f')
                level = jsonData[i]['levels'][keywords[k]][j]['level']
                level_val = dic_level_val[level]
                seconds = int(jsonData[i]['levels'][keywords[k]][j]['seconds'])
    
                dt_list.append(dt)
                level_list.append(level)
                leval_list.append(level_val)
                seconds_list.append(seconds)
                type_list.append(log_type)

        df_dt = pd.DataFrame(data=dt_list, columns=['datetime'])
        df_level = pd.DataFrame(data=level_list, columns=['level'])
        df_leval = pd.DataFrame(data=leval_list, columns=['level_val'])
        df_seconds = pd.DataFrame(data=seconds_list, columns=['seconds'])
        df_type = pd.DataFrame(data=type_list, columns=['logtype'])

        df = pd.concat([df_dt,df_level,df_leval, df_seconds, df_type], ignore_index=False, axis=1)
        df = df.set_index('datetime', drop=True)
        df = df.sort_index()
        print(df)

        if k == 0: df_data = df
        if k == 1: df_short = df

    return df_data, df_short


def main_routine():
    global dt_list

    path_PhysAct = 'Physical Activity'
    path_SpO2 = 'Other'
    path_Sleep = 'Sleep'

    for dirname in dirlist:
        pngbase = dirname + "_fitbit.png"
        pngfile = os.path.join(dirname, pngbase)

        path_fitbit = os.path.join(dirname,'fitbit')

        if os.path.exists(path_fitbit) == False:
            print(dirname, " doesn't have fitbit directory.")
            continue
        #--------------------------------------
        #グラフを全部描き直す時はこのブロックをコメントアウト
        if os.path.exists(pngfile):
            print(pngfile, " already exists.")
            continue
        #--------------------------------------

        print("Processing ", path_fitbit)

        try:
#--------------------Heart Rate-----------------
            search_path = os.path.join(path_fitbit, path_PhysAct, "heart_rate-*")
            df = read_HeartRate(search_path)
#--------------------Activity-----------------
            search_path = os.path.join(path_fitbit, path_PhysAct)
            df1 = read_Activity(search_path)
#--------------------SpO2-----------------
            search_path = os.path.join(path_fitbit, path_SpO2, "estimated_oxygen_variation-*")
            df2 = read_SpO2(search_path)
        except:
            print(RED + "Exception: Something bad." + END)
            continue

#--------------------Sleep-----------------
        search_path = os.path.join(path_fitbit, path_Sleep, "sleep-*")
        df3, df4 = read_Sleep(search_path)

#--------------------Plot-----------------

        fig = plt.figure(tight_layout=True, figsize=(12,10))
        ax1 = fig.add_subplot(311, title='fitbit - [Heart rate]', ylabel='BPM')
        ax2 = fig.add_subplot(312, title='fitbit - [Activity]', ylabel='min.')
        ax3 = fig.add_subplot(313, title='fitbit - [Estimated Oxgen Val.]', ylabel='RAW ratio')
        ax3a = ax3.twinx()
        ax3a.set_ylabel('%')

        # Maximum Window
        xmin = min([df.index[0], df1.index[0], df2.index[0]])
        xmax = max([df.index[len(df)-1], df1.index[len(df1)-1], df2.index[len(df2)-1]])
        # Minimum Window
        #xmin = max([df.index[0], df1.index[0], df2.index[0]])
        #xmax = min([df.index[len(df)-1], df1.index[len(df1)-1], df2.index[len(df2)-1]])
        # Hart Rate Window
        #xmin = df.index[0]
        #xmax = df.index[len(df)-1]

        for a in [ax1,ax2, ax3, ax3a]:
            a.xaxis.set_major_formatter(md.DateFormatter('%d-%b'))
            a.xaxis.set_major_locator(md.DayLocator(interval=2,tz=JST))
            a.xaxis.set_minor_locator(md.HourLocator(byhour=range(0,24,6),tz=JST))
            a.set_xlim([xmin,xmax])

        ax1.scatter(df.index,df['bpm'], s=0.5, color='gray',label='HR')
        ax1.plot(df.index,df['mean'],color='red',label='Mean')

        ax2.stackplot(df1.index,df1['sedentary'],df1['lightly_active'],df1['moderately_active'],df1['very_active'],labels = activities)

        ax3.scatter(df2.index,df2['R'], s=0.5, color='black',label='IR/R')
        ax3a.scatter(df2.index,df2['eov'], s=0.1, color='blue',label='EOV')
        ax3a.plot(df2.index,df2['m_eov'],'--',color='red',label='Mean_EOV')
       #ax3a.scatter(df2.index,df2['m_eov'], s=0.5, color='red',label='Mean_EOV')

        plt.gcf().autofmt_xdate()

        ax1.legend(loc='upper right',fontsize=12)
        ax2.legend(loc='upper right',fontsize=8)

        h1, l1 = ax3.get_legend_handles_labels()
        h2, l2 = ax3a.get_legend_handles_labels()
        ax3a.legend(h1+h2, l1+l2, loc='upper right',fontsize=12)

        plt.savefig(pngfile, dpi=200, bbox_inches="tight", pad_inches=0.1)


if __name__ == "__main__": 
    main_routine() 