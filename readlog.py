# 外部モジュールのインポート
# import [モジュール名]
# as [ニックネーム(任意)]
# from [package] import [module] 特定の関数しか使わない時
import glob   # ファイル検索する
import os     # OSの機能使う
import struct # バイナリファイル扱う
import pandas as pd  # データベース扱う
from datetime import timedelta  # 日付時刻データ扱う
import re     # 正規表現扱う（条件指定など）
import shutil # ファイル操作する

###############################
# Read log file
###############################
osep = os.sep  # OSごとに異なるPATHの区切り文字を取得
# Windows の場合は"¥"か"\"が得られる
# Mac / Linuxだと"/"

orids = []  # 変数宣言（予約）
# orids には"OR"で始まる（下で定義）フォルダのリストが格納される
# @@@@@@ ここは変える必要あり
orids = glob.glob("OR*")  # Get parent folder names (OR-**) represent trialists.
# @@@@@@

log_order = [8,40,8,8,4,2,2,2,2,2]   # Log file structure
log_use   = [1, 0,1,0,1,1,1,1,1,1]   # Bit for data will be used

# CSVファイルに書き出すデータ構造を作成（とりま空っぽ）
df = pd.DataFrame(data=None, index=None, columns=["orid", "dateid", "date_time", "hashid", "card_id", "inst", "org_file"], dtype=str)

print(orids)
# len(orids)はORのつくフォルダの数
for n_orid in range(len(orids)):  # Process each trialist individually
    orid = orids[n_orid] #n_orid番目の"OR"フォルダ名
    logfiles = [] # 変数宣言（予約）= リスト
    # ["ORxxxx" + "¥" + "**" + "¥" + "*.LOG"]
    # ORxxxxというフォルダの下の任意のフォルダ(**)の下の.LOGファイルを探す
    # recursive=True 下層のフォルダまで繰り返す
    logfiles = glob.glob(orid + osep + "**" + osep + "*.LOG", recursive=True)  # Get all LOG files
    print(logfiles)
    
    for n_log in range(len(logfiles)):    # Process each file
        filepath = logfiles[n_log]        # get each file path
        basename_wo_ext = os.path.splitext(os.path.basename(filepath))[0]  # Get hash characters

        with open(filepath, 'rb') as f:       # Open a file
            print("Loading " + filepath)
            rawdata = []
            rawdata.append(orid)              # [OR-****]
            rawdata.append(basename_wo_ext)   # [OR-****, CJ******]
            count = 0                         # Counter for bit
            for length in log_order:
                data = []
                for i in range(length):
                    bytes = f.read(1)         # Read 1 byte
                    if bytes != 0:
                        data.append(struct.unpack('<c', bytes)[0].decode("UTF-8"))
                    else:
                        break
                token = ''.join(data).strip('\x00')
                if log_use[count] == 1:
                    rawdata.append(token)
                count += 1                   # Bit count up

            logdata = []                     # Create output log data with our format
            logdata.append(rawdata[0])
            logdata.append(''.join(rawdata[4:7]))
            logdata.append('-'.join(rawdata[4:7])+' '+':'.join(rawdata[7:10]))            
            logdata.append(rawdata[1])
            logdata.append(rawdata[3])
            logdata.append(rawdata[2])
            logdata.append(filepath)
            row = pd.Series(logdata, index=df.columns)   # Convert to pandas data series
            df = df.append(row, ignore_index=True)       # Add to dataframe

df['date_time'] = df['date_time'].astype('datetime64[ns]')
df = df.sort_values(['orid','date_time'], ascending=[True, True]) # Sort data by orid, date
df.reset_index(inplace=True, drop=True)
df.to_csv('result_4ck.csv', index=False)                 # Output raw data to csv

#################################
# Check 180 days
#################################
orids = sorted(df["orid"].unique())  # Make a list of trialists
tdelta = timedelta(days=180)         # Define 180 days

for i in range(len(orids)):          # Process each trialist individually

    task = df[df['orid'] == orids[i]].copy()               # Extract one patient from whole data.
    task['t-shift'] = task['date_time'].shift(-1)          # Add temporal column to calc time delta
    task['tdiff'] = (task['t-shift'] - task['date_time'])  # Calc time delta
    task = task.drop('t-shift', axis=1)                    # Remove temporal column

    task['No'] = ""
    task['base_name'] = ""
    serial_num = pd.RangeIndex(start=1, stop=len(task[task['tdiff'] >= tdelta].index) + 1, step=1)  # Count number of available data
    task.loc[task['tdiff'] >= tdelta, 'No'] = serial_num.astype("str").str.zfill(2)     # Check 180 days, filter data, add "No." column
    task.loc[task['No'] != '', 'base_name'] = task['orid'].astype("str") + "_" + task["No"] + "_" + task["dateid"].astype("str")  # Add "base_name" column

    # Combine each lists to one
    if i == 0:
        result = task.copy()
    elif i > 0:
        result = pd.concat([result, task])


# Change order
result = result[["orid", "dateid", "date_time", "hashid", "card_id", "inst", "tdiff", "No", "base_name", "org_file"]]
result.to_csv('result_all.csv', index=False)    # Output all results to csv

# Check 180 days, filter data, output filtered results to csv
result[result['tdiff'] >= tdelta].to_csv('result_180.csv', index=False)  

print(result)


#############################
# Convert file names
#############################
# 自分(readlog.py)のいるディレクトリと並列の階層に"PROC"ディレクトリを作成する
# そのために、PROCディレクトリのパス名を作成する
current_path = os.getcwd()
parent_path = os.path.dirname(current_path)
dist_path = parent_path + osep + "PROC"

if os.path.exists(dist_path):
    # もしPROCが既に存在したら、メッセージを出すだけ
    print(dist_path + " is already exists.")
else:
    # PROCを作成
    os.mkdir(dist_path)
    print("Created " + dist_path)

proc_table = result.loc[result['tdiff'] >= tdelta, ['orid', 'hashid', 'base_name']].copy()
print(proc_table)
orids = sorted(proc_table["orid"].unique())    # Make a list of trialists

raw_all = []
proc_all = []
for n_orid in range(len(orids)):  # Process each trialist individually
    proc_files = []
    orid = orids[n_orid]
    slice_proc_table = proc_table.loc[proc_table['orid'] == orid, ['hashid', 'base_name']].copy()
    slice_proc_table = slice_proc_table.set_index('hashid', drop=True)
    dic_table = slice_proc_table.to_dict()

    raw_files = []
    raw_files = glob.glob(orid + osep + "**" + osep + "*.*", recursive=True)  # Get all files
    
    for r_file in raw_files:                      # Process each file individually
        replacements = dic_table['base_name']     # Dictionary for translate file name
        new_name = re.sub('({})'.format('|'.join(map(re.escape, replacements.keys()))), lambda m: replacements[m.group()], r_file)
        proc_files.append(new_name)

    raw_all.extend(raw_files)    # Make all lists to one
    proc_all.extend(proc_files)

convert_table = pd.DataFrame({'raw':raw_all,'proc':proc_all})    # Create pandas dataframe from file lists
convert_table = convert_table[convert_table['raw'] != convert_table['proc']]  # Filter data
convert_table = convert_table.sort_values('proc', ascending=True)
convert_table.to_csv('convert_file_name.csv', index=False)       # Output file name convert table to csv.

###################
# Copy files
###################
def yes_no_input():    # Function for YES/NO input.
    while True:
        choice = input("Do you want to make a copies? [y/N]: ").lower()
        if choice in ['y', 'ye', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False

if yes_no_input():
    file_num = len(convert_table)
    for i in range(file_num):
        progress = (100 * i / file_num)                           # Calc progress [%]
        org = current_path + osep + str(convert_table.iloc[i,0])  # Original file path
        dist = dist_path + osep + str(convert_table.iloc[i, 1])   # New file path
        os.makedirs(os.path.dirname(dist), exist_ok=True)         # Make directories for new files
        print(org + " -> " + dist + " [" + str(i) +"/"+ str(file_num) +" ("+format(progress, '5.1f')+"%)" + "]", end="")
        if os.path.isfile(org) and (not os.path.exists(dist)):    # Process if it is a file (except directory) and new.
            shutil.copy2(org, dist)                               # Copy file
            print(" copied.")
        else:
            print(" passed.")
