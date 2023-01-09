# -*- coding: utf-8 -*-
import json
from datetime import datetime, timedelta, timezone
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
import glob
import os

JST = timezone(timedelta(hours=+9), 'JST')

dirlist = glob.glob("EPW*")

print(dirlist)

for dirname in dirlist:

   path_fitbit = os.path.join(dirname,'fitbit')
   path_PhysAct = 'Physical Activity'
   path_SpO2 = 'Other'

#--------------------Heart Rate-----------------
   hr_jsons = []
   search_path = os.path.join(path_fitbit, path_PhysAct, "heart_rate-*")
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

#--------------------Activity-----------------
   j=0
   activities = ['sedentary','lightly_active','moderately_active','very_active']
   middlen = '_minutes'
   activ_min_f = []
   am_list = []

   for activity in activities:
       j = j + 1
       job = activity + middlen + "*"
       search_path = os.path.join(path_fitbit, path_PhysAct, job)
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

#--------------------SpO2-----------------
   eov_csvs = []
   search_path = os.path.join(path_fitbit, path_SpO2, "estimated_oxygen_variation-*")
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

   def conv_eov(x):
       result = x * (0.1) + 97  #formula from "fitbit forum (2020)"

       if result > 100:
           result = 100
       elif result < 0:
           result = 0
       else:
           pass

       return result

   df2['eov'] = df2['R'].apply(conv_eov)
   df2['m_eov'] = df2['eov'].rolling(100).mean()

   print(df2)
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

   pngfile = os.path.join(dirname, 'fitbit.png')
   plt.savefig(pngfile, dpi=200, bbox_inches="tight", pad_inches=0.1)
