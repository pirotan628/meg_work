#from glob import glob   # ファイル検索する
import glob   # ファイル検索する
import os     # OSの機能使う
import struct # バイナリファイル扱う
import pandas as pd  # データベース扱う
from datetime import timedelta  # 日付時刻データ扱う
import re     # 正規表現扱う（条件指定など）
import shutil # ファイル操作する
from pathlib import Path

# EEGのヘッダーを読む関数
#def readeeg(filepath):
#    eeg_order = [8,2,6,16,8,8,8,8,4,2,2,2,2,2]   # EEG file structure
#    eeg_use   = [1,0,0, 0,1,0,1,0,1,1,1,1,1,1]   # Bit for data will be used
# "orid", "dateid", "date_time", "hashid", "card_id", "inst", "org_file"
#    orid = "OR-xxx"
#    basename_wo_ext = os.path.splitext(os.path.basename(filepath))[0]  # Get hash characters
#    base_name=(Path(file_path).name)
#    with open(filepath, 'rb') as f:       # Open a file
#        error_flag = 0
#        print("Loading " + filepath)
#        rawdata = []
#        rawdata.append(orid)              # [OR-****]
#        rawdata.append(basename_wo_ext)   # [OR-****, CJ******]
#        count = 0                         # Counter for bit
#        for length in eeg_order:
#            data = []
#            for i in range(length):
#                bytes = f.read(1)         # Read 1 byte
#                if bytes != 0:
#                    try:
#                        data.append(struct.unpack('<c', bytes)[0].decode("UTF-8"))
#                    except:
#                        error_flag = -1
#                else:
#                    break
#
#            token = ''.join(data).strip('\x00')    # extracted word
#            if eeg_use[count] == 1:                # if use word
#                rawdata.append(token)
#
#            count += 1                   # Bit count up
#
#        if error_flag == -1: print("Read Error")
#
#        header = []                     # Create output log data with our format
#        header.append(rawdata[0])                                          # eeg-name
#        header.append(rawdata[1])                                          # inst
#        header.append(rawdata[2])                                          # pnt-name
#        header.append(rawdata[3])                                          # card-id
#        header.append(''.join(rawdata[4:7]))                               # date-id
#        header.append('-'.join(rawdata[4:7])+' '+':'.join(rawdata[7:10]))  # date_time         
#        header.append(base_name)                                          # file-name
#
#    return header

# LOGのヘッダーを読む関数
def readlog(filepath):
    log_order = [8,2,6,8,8,16,8,8,4,2,2,2,2,2]   # Log file structure
    log_use   = [1,0,0,1,0, 0,1,0,1,1,1,1,1,1]   # Bit for data will be used
# "orid", "dateid", "date_time", "hashid", "card_id", "inst", "org_file"
#    orid = "OR-xxx"
    basename_wo_ext = os.path.splitext(os.path.basename(filepath))[0]  # Get hash characters
    base_name=(Path(file_path).name)
    with open(filepath, 'rb') as f:       # Open a file
        error_flag = 0
        print("Loading " + filepath)
        rawdata = []
#        rawdata.append(orid)              # [OR-****]
        rawdata.append(basename_wo_ext)   # [OR-****, CJ******]
        count = 0                         # Counter for bit
        for length in log_order:
            data = []
            for i in range(length):
                bytes = f.read(1)         # Read 1 byte
                if bytes != 0:
                    try:
                        data.append(struct.unpack('<c', bytes)[0].decode("UTF-8"))
                    except:
                        error_flag = -1
                else:
                    break

            token = ''.join(data).strip('\x00')    # extracted word
            if log_use[count] == 1:                # if use word
                rawdata.append(token)

            count += 1                   # Bit count up


        if error_flag == -1: print("Read Error")

        header = []                     # Create output log data with our format
        header.append(rawdata[0])                                          # log-name
        header.append(rawdata[1])                                          # inst
        header.append(rawdata[2])                                          # pnt-name
        header.append(rawdata[3])                                          # card-id
        header.append(''.join(rawdata[4:7]))                               # date-id
        header.append('-'.join(rawdata[4:7])+' '+':'.join(rawdata[7:10]))  # date_time         
        header.append(base_name)                                           # file-name
        header.append(''.join(rawdata[4:7])+''.join(rawdata[7:9]))         # new-filename

    return header    

###########################
# MAIN
###########################
#orids = []  # 変数宣言（予約）

# CSVファイルの構成
df = pd.DataFrame(data=None, index=None, columns=["idname", "inst", "hashid", "card_id", "date-id", "date-time","filename", "new_filename"], dtype=str)

# 置いたところ以下全部調査
all_file_list = glob.glob("**", recursive=True)  # All file list in this directory

for file_path in all_file_list:
    root, extraw = os.path.splitext(file_path)  #ファイル名（パス有り）と拡張子の取得
    ext = extraw.lower()                  #判定用の拡張子の小文字化
    print(root, extraw, ext)
    #if ext == '.eeg':
    #    header = readeeg(file_path) 
    #    row = pd.Series(header, index=df.columns)   # Convert to pandas data series
    #    df = df.append(row, ignore_index=True)       # Add to dataframe
    if ext == '.log':
        print(file_path)
        header = readlog(file_path)
        row = pd.Series(header, index=df.columns)   # Convert to pandas data series
        df = df.append(row, ignore_index=True)       # Add to dataframe

# データの整理（ソート、重複削除）
df.sort_values(by=['hashid','idname'], ascending=True, inplace=True)
df.drop_duplicates(inplace=True)

print(df)
df.to_csv('sortingtest.csv', index=False)       # Output file name convert table to csv.

#############################
# Convert file names
#############################
 #-------------------------------------------------------
 # ソートしたファイルの新しい置き場のフォルダとして"SORT"を作る
 # 例えばEPWが　c:¥brabra¥hogehoge¥EPW　にあるとき
 # c:¥brabra¥hogehoge¥SORT に置きたいとする

current_path = os.getcwd()                      # current_path =　c:¥brabra¥hogehoge¥EPW
parent_path = os.path.dirname(current_path)     # parent_path = c:¥brabra¥hogehoge
dest_path = os.path.join(parent_path, "SORT")   # dest_path = c:¥brabra¥hogehoge¥SORT

if os.path.exists(dest_path):                  
    print(dest_path + " is already exists.")
else:
    os.mkdir(dest_path)
    print("Created " + dest_path)
#-------------------------------------------------------

# 名前を変えたいファイルを探す
# 全部のファイルのリストは既に持っている。
# それは all_file_list である

#辞書を作る
import itertools
l_2d=df[['idname','new_filename']].to_numpy().tolist()
l_1d=list(itertools.chain.from_iterable(l_2d))
dict_name = {l_1d[i]: l_1d[i + 1] for i in range(0, len(l_1d), 2)}
print(dict_name)


# all_file_list の中から、csvファイルのidnameのカラムに該当するファイルを探す
for file_path in all_file_list:   
    base = os.path.basename(file_path)          #ファイル名（パス無し, 拡張子あり）
    root, extraw = os.path.splitext(base)  #ファイル名（パス有り, 拡張子無し）と拡張子の取得
    ext = extraw.lower()                  #判定用の拡張子の小文字化
    new_file_base_df = df.loc[df['idname']==root, 'new_filename']  # YJxxxxx から YYmmddHHMM を探しあてる    

#    try:
#       new_file_base = new_file_base_df.values[:1][0]
#    except:
#        if ext != ".ptn":
#            print("No log file for this file: "+file_path)

#    print(base, root, extraw, ext, new_file_base_df)
#    org_file = os.path.join(current_path, base)

    org_file = os.path.join(current_path, file_path)
    new_file=file_path
    for x, y in dict_name.items():
        new_file = new_file.replace(x, y)
        if x in file_path: new_file_base = y

    new_file_path = os.path.join(dest_path,new_file_base,new_file)
    print(org_file + " --> " + new_file_path)

#def yes_no_input():    # Function for YES/NO input.
#    while True:
#        choice = input("Do you want to make a copies? [y/N]: ").lower()
#        if choice in ['y', 'ye', 'yes']:
#            return True
#        elif choice in ['n', 'no']:
#            return False

# if yes_no_input():
    if os.path.isfile(org_file):                                   # Process if it is a file (except directory).
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)         # Make directories for new files
        shutil.copy2(org_file, new_file_path)                               # Copy file
#


#    try:
#       new_file_base = new_file_base_df.values[:1][0]
#       new_filename = str(new_file_base + extraw)
#       new_file_path = os.path.join(dest_path, new_filename)
#       org_file = os.path.join(current_path, base)
#       print(org_file + " --> " + new_file_path)
#       print(base, root, extraw, ext, new_file_path)
#    except:
#       print("No log file for this file: "+file_path)





#proc_table = result.loc[['hashid', 'date-id']].copy()
#print(proc_table)
#orids = sorted(proc_table["date-id"].unique())    # Make a list of trialists
#
#raw_all = []
#proc_all = []
#for n_orid in range(len(orids)):  # Process each trialist individually
#    proc_files = []
#    orid = orids[n_orid]
#    slice_proc_table = proc_table.loc[proc_table['orid'] == orid, ['hashid', 'base_name']].copy()
#    slice_proc_table = slice_proc_table.set_index('hashid', drop=True)
#    dic_table = slice_proc_table.to_dict()

#    raw_files = []
#    raw_files = glob.glob(orid + osep + "**" + osep + "*.*", recursive=True)  # Get all files
    
#    for r_file in raw_files:                      # Process each file individually
#        replacements = dic_table['base_name']     # Dictionary for translate file name
#        new_name = re.sub('({})'.format('|'.join(map(re.escape, replacements.keys()))), lambda m: replacements[m.group()], r_file)
#        proc_files.append(new_name)

#    raw_all.extend(raw_files)    # Make all lists to one
#    proc_all.extend(proc_files)

#convert_table = pd.DataFrame({'raw':raw_all,'proc':proc_all})    # Create pandas dataframe from file lists
#convert_table = convert_table[convert_table['raw'] != convert_table['proc']]  # Filter data
#convert_table = convert_table.sort_values('proc', ascending=True)
#convert_table.to_csv('convert_file_name.csv', index=False)       # Output file name convert table to csv.

###################
# Copy files
###################
#def yes_no_input():    # Function for YES/NO input.
#    while True:
#        choice = input("Do you want to make a copies? [y/N]: ").lower()
#        if choice in ['y', 'ye', 'yes']:
#            return True
#        elif choice in ['n', 'no']:
#            return False

#if yes_no_input():
#    file_num = len(convert_table)
#    for i in range(file_num):
#        progress = (100 * i / file_num)                           # Calc progress [%]
#        org = current_path + osep + str(convert_table.iloc[i,0])  # Original file path
#        dist = dist_path + osep + str(convert_table.iloc[i, 1])   # New file path
#        os.makedirs(os.path.dirname(dist), exist_ok=True)         # Make directories for new files
#        if os.path.isfile(org):                                   # Process if it is a file (except directory).
#            shutil.copy2(org, dist)                               # Copy file
#            print(org + " -> " + dist + " [" + str(i) +"/"+ str(file_num) +" ("+format(progress, '5.1f')+"%)" + "]")
