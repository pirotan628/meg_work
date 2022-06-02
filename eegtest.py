import glob   # ファイル検索する
import os     # OSの機能使う
import struct # バイナリファイル扱う
import pandas as pd  # データベース扱う
from datetime import timedelta  # 日付時刻データ扱う
import re     # 正規表現扱う（条件指定など）
import shutil # ファイル操作する
from pathlib import Path

# EEGのヘッダーを読む関数
def readeeg(filepath):
    eeg_order = [8,2,6,16,8,8,8,8,4,2,2,2,2,2]   # EEG file structure
    eeg_use   = [1,0,0, 0,1,0,1,0,1,1,1,1,1,1]   # Bit for data will be used
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
        for length in eeg_order:
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
            if eeg_use[count] == 1:                # if use word
                rawdata.append(token)

            count += 1                   # Bit count up

        if error_flag == -1: print("Read Error")

        header = []                     # Create output log data with our format
        header.append(rawdata[0])                                          # eeg-name
        header.append(rawdata[1])                                          # inst
        header.append(rawdata[2])                                          # pnt-name
        header.append(rawdata[3])                                          # card-id
        header.append(''.join(rawdata[4:7]))                               # date-id
        header.append('-'.join(rawdata[4:7])+' '+':'.join(rawdata[7:10]))  # date_time         
        header.append(base_name)                                          # file-name

    return header

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
        header.append(base_name)                                          # file-name

    return header    

###########################
# MAIN
###########################
orids = []  # 変数宣言（予約）

# 調査範囲を限定する場合
#orids = glob.glob("OR*")  # Get parent folder names (OR-**) represent trialists.
#orids = glob.glob("PROC*")  # Get parent folder names (OR-**) represent trialists.

# 置いたところ以下全部調査
orids = glob.glob("*")  # Get parent folder names (OR-**) represent trialists.

# 今のところ不使用
#extlist = ['.eeg', '.elp', '.mul', '.log', '.evt']  # 必要な拡張子リスト、小文字
#extlist = ['.eeg','.log']  # 必要な拡張子リスト、小文字
#ignorelist = ['.ptn', '.11d', '.21e', '.cmt', '.cn2', '.eg2', '.eg_', '.pnt']   # 除外リスト

# CSVファイルの構成
df = pd.DataFrame(data=None, index=None, columns=["idname", "inst", "hashid", "card_id", "date-id", "date-time","filename"], dtype=str)

# 調査開始
for n_orid in range(len(orids)):  # Process each trialist individually
    orid = orids[n_orid] #n_orid番目のフォルダ名
    path_name = os.path.join(orid, "**", "*.*")
    all_file_list = glob.glob(path_name, recursive=True)  # All file list in OR*
    for file_path in all_file_list:
        root, extraw = os.path.splitext(file_path)  #ファイル名（パス有り）と拡張子の取得
        ext = extraw.lower()                  #判定用の拡張子の小文字化
        if ext == '.eeg':
            header = readeeg(file_path) 
            row = pd.Series(header, index=df.columns)   # Convert to pandas data series
            df = df.append(row, ignore_index=True)       # Add to dataframe
        elif ext == '.log':
            header = readlog(file_path)
            row = pd.Series(header, index=df.columns)   # Convert to pandas data series
            df = df.append(row, ignore_index=True)       # Add to dataframe

# データの整理（ソート、重複削除）
df.sort_values(by=['hashid','idname'], ascending=True, inplace=True)
df.drop_duplicates(inplace=True)

print(df)
df.to_csv('eegtest.csv', index=False)       # Output file name convert table to csv.