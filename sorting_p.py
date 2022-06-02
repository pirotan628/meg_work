import glob   # ファイル検索する
import os     # OSの機能使う
import struct # バイナリファイル扱う
import pandas as pd  # データベース扱う
from datetime import timedelta  # 日付時刻データ扱う
import re     # 正規表現扱う（条件指定など）
import shutil # ファイル操作する
from pathlib import Path
import sys


#############################
# 新しいファイルだけコピーする関数
#############################
def copy_new(source, destination, sentence):
    os.makedirs(os.path.dirname(destination), exist_ok=True)         # Make directories for new files
        
    if os.path.isfile(source) and (not os.path.exists(destination)):    # Process if it is a file (except directory) and new.
        shutil.copy2(source, destination)                               # Copy file
        sys.stderr.write(("Copy:" + sentence +'\n'))
    else:
        sys.stderr.write(("File exists:" + sentence +'\n'))

#############################
# YES/NO input. の関数
#############################
def yes_no_input():
    while True:
        choice = input("Do you want to make a copies? [y/N]: ").lower()
        if choice in ['y', 'ye', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False

#############################
# EEGのヘッダーを読む関数
#############################
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

#############################
# LOGのヘッダーを読む関数
#############################
def readlog(filepath):
    log_order = [8,2,6,8,8,16,8,8,4,2,2,2,2,2]   # Log file structure
    log_use   = [1,0,0,1,0, 0,1,0,1,1,1,1,1,1]   # Bit for data will be used

    basename_wo_ext = os.path.splitext(os.path.basename(filepath))[0]  # Get hash characters
    base_name=(Path(file_path).name)
    with open(filepath, 'rb') as f:       # Open a file
        error_flag = 0
        print("Loading " + filepath)
        rawdata = []
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
# CSVファイルの構成
# Pandas DataFrame を使う
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


# csvの表から名前変換用の辞書を作る
l_1d_key = df['idname'].to_numpy().tolist()        # キー(YJxxxxx)のリスト
l_1d_val = df['new_filename'].to_numpy().tolist()  # 値(YYmmddHHMM)のリスト
dict_name = dict(zip(l_1d_key, l_1d_val))          # 2つのリストから辞書を作成

print(dict_name)

#yes_to_copy = True                # 問答無用でコピーする時, yes <- True
yes_to_copy = yes_no_input()      # Yes/No でコピーするか決めたい時, yes <- True, No <- False

# 名前を変えたいファイルを探す
# 全部のファイルのリストは既に持っている。
# それは all_file_list である
for file_path in all_file_list:   
    # 辞書の中から、csvファイルのidnameのカラムに該当するファイルを探す
    new_file=file_path
    for x, y in dict_name.items():
        if x in file_path:      # YJxxxxx から YYmmddHHMM を探しあてる
            new_file_base = y   # フォルダ作成のため YYmmddHHMM を保管
            new_file = new_file.replace(x, y)   # YJxxxxx から YYmmddHHMM に置き換え

    #コピー元とコピー先のパス名を生成
    org_file = os.path.join(current_path, file_path)
    new_file_path = os.path.join(dest_path,new_file_base,new_file)

    sentence = org_file + " --> " + new_file_path    # 表示用の文字列を作成

    if  yes_to_copy:                     # コピーがyesなら
        copy_new(org_file, new_file_path, sentence)  # 新しいファイルだけコピー（上の関数）
    else:
        print("No copy: " + sentence)    # コピーがNoなら、コピーしない旨を表示
