# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta, timezone
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
import glob
import os

#赤文字表示に使う定数
RED = '\033[31m'
END = '\033[0m'

#時刻データのための日本標準時定義
JST = timezone(timedelta(hours=+9), 'JST')

#検索用するフォルダのリスト
dirlist = glob.glob("Epw*")
dirlist += glob.glob("epw*")
dirlist += glob.glob("EPW*")

# 各データの保存先フォルダ
path_PhysAct = 'Physical Activity'
path_SpO2 = 'Other'
path_Sleep = 'Sleep'

#Activitiesフォルダのファイル名リスト
activities = ['sedentary','lightly_active','moderately_active','very_active']

print(dirlist)

#心拍データを読むサブルーチン
def read_HeartRate(search_path):
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

#活動量を読むサブルーチン
def read_Activity(search_path_base):
    j=0
    middlen = '_minutes'
    activ_min_f = []
    am_list = []
    dt_list = []

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

#fitbit3の独自データから血中酸素濃度を求める関数
def conv_eov(x):

    result = x * (0.1) + 97  #formula from "fitbit forum (2020)"

    if result > 100:
        result = 100
    elif result < 0:
        result = 0
    else:
        pass

    return result

#血中酸素濃度のデータを読むサブルーチン
def read_SpO2(search_path):
    eov_csvs = []
    eov_csvs = glob.glob(search_path)

    # Otherが存在しない場合の処理
    if eov_csvs == []:
        cols = ['timestamp','eov','m_eov']
        df = pd.DataFrame(index=[], columns=cols)
        df.set_index('timestamp', drop=True)
        return df

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

#睡眠データを読むサブルーチン
def read_Sleep(search_path):
    keywords = ['data', 'shortData']
    dic_level_val = {'deep':0, 'light':1, 'rem':2, 'wake':3, 'asleep':0, 'restless':1, 'awake':2}

    slp_jsons = glob.glob(search_path)

    #Sleepのjsonが無い場合
    if slp_jsons == []:
        cols = ['datetime','levels','level_val','seconds','logtype']
        df = pd.DataFrame(index=[], columns=cols)
        df.set_index('datetime', drop=True)
        return df, df, df

    f = open(slp_jsons[0] ,'r')
    jsonData = json.load(f)

    for k in range(len(keywords)):
        dt_list = []
        level_list = []
        leval_list = []
        seconds_list = []
        type_list = []


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
                
    df_classic = df_data[df_data['logtype']=='classic']
    df_data = df_data[df_data['logtype']=='stages']

    return df_data, df_short, df_classic

#メインルーチン
def main_routine():
    for dirname in dirlist:        #[Epw****] を順に探索
        pngbase = dirname + "_fitbit.png"
        pngfile = os.path.join(dirname, pngbase)   #PNGファイルのフルパスを生成
        
        path_fitbit = os.path.join(dirname,'fitbit') #fitbitデータのある場所を検索

        if os.path.exists(path_fitbit) == False:  # "fitbit" フォルダが見つからない場合
            print(dirname, " doesn't have fitbit directory.")
            continue     #この被験者はパスして次の人に進む
        #--------------------------------------
        #グラフを全部描き直す時はこのブロックをコメントアウト
        if os.path.exists(pngfile):     #既にグラフがある場合
            print(pngfile, " already exists.")
            continue   #この被験者はパスして次の人に進む
        #--------------------------------------

        print("Processing ", path_fitbit)

        try:  #データを読むサブルーチンを実行
#--------------------Heart Rate-----------------
            search_path = os.path.join(path_fitbit, path_PhysAct, "heart_rate-*")
            df = read_HeartRate(search_path)
#--------------------Activity-----------------
            search_path = os.path.join(path_fitbit, path_PhysAct)
            df1 = read_Activity(search_path)
#--------------------SpO2-----------------
            search_path = os.path.join(path_fitbit, path_SpO2, "estimated_oxygen_variation-*")
            df2 = read_SpO2(search_path)
#--------------------Sleep-----------------
            search_path = os.path.join(path_fitbit, path_Sleep, "sleep-*")
            df3, df4, df5 = read_Sleep(search_path)
        except:    #何かエラーが出てしまった場合
            print(RED + "Exception: Something bad." + END)
            continue  #この被験者はパスして次の人に進む

#--------------------Plot-----------------

        fig = plt.figure(tight_layout=True, figsize=(12,10))
        ax1 = fig.add_subplot(411, title='fitbit - [Heart rate]', ylabel='BPM')
        ax2 = fig.add_subplot(412, title='fitbit - [Activity]', ylabel='min.')
        ax3 = fig.add_subplot(413, title='fitbit - [Estimated Oxgen Val.]', ylabel='RAW ratio')
        ax3a = ax3.twinx()
        ax3a.set_ylabel('%')
        ax4 = fig.add_subplot(414, title='fitbit - [Sleep]', ylabel='level')

    # Maximum Window
#        xmin = min([df.index[0], df1.index[0], df2.index[0]])
#        xmax = max([df.index[len(df)-1], df1.index[len(df1)-1], df2.index[len(df2)-1], df3.index[len(df3)-1]])
#        xmax = max([df.index[len(df)-1], df1.index[len(df1)-1], df2.index[len(df2)-1]])
    # Minimum Window
        #xmin = max([df.index[0], df1.index[0], df2.index[0]])
        #xmax = min([df.index[len(df)-1], df1.index[len(df1)-1], df2.index[len(df2)-1]])
    # Hart Rate Window
        #xmin = df.index[0]
        #xmax = df.index[len(df)-1]
    # Activity Window
        xmin = df1.index[0]
        xmax = df1.index[len(df1)-1]

        for a in [ax1,ax2, ax3, ax3a,ax4]:
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
        ax4.scatter(df3.index, df3['level_val'], s=3, color='blue', label='stages-data')
        ax4.scatter(df4.index, df4['level_val'], s=3, color='red', label='stages-short')
        ax4.scatter(df5.index, df5['level_val'], s=3, color='green', label='classic')

        plt.gcf().autofmt_xdate()

        ax1.legend(loc='upper right',fontsize=12)
        ax2.legend(loc='upper right',fontsize=8)

        h1, l1 = ax3.get_legend_handles_labels()
        h2, l2 = ax3a.get_legend_handles_labels()
        ax3a.legend(h1+h2, l1+l2, loc='upper right',fontsize=12)
        
        ax4.legend(loc='upper right', fontsize=12)

        plt.savefig(pngfile, dpi=200, bbox_inches="tight", pad_inches=0.1)

#お約束（単独実行時にメインルーチンを実行）
if __name__ == "__main__": 
    main_routine() 