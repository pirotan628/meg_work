############################################### 
# megtools.py
# データ整理で良く使う関数のまとめ
# ------------------------------------------
# pythonスクリプトと同一ディレクトリに置き、
# from megtools import *
# でインポート
# ------------------------------------------
############################################### 

import os
import sys
import shutil
from pathlib import Path

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
def readeeg(filepath):
    eeg_order = [8,2,6,16,8,8,8,8,4,2,2,2,2,2]   # EEG file structure
    eeg_use   = [1,0,0, 0,1,0,1,0,1,1,1,1,1,1]   # Bit for data will be used

    basename_wo_ext = os.path.splitext(os.path.basename(filepath))[0]  # Get hash characters
    base_name=(Path(filepath).name)
    with open(filepath, 'rb') as f:       # Open a file
        error_flag = 0
        print("Loading " + filepath)
        rawdata = []
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
        header.append(''.join(rawdata[4:7])+''.join(rawdata[7:9]))         # new-filename

    return header

#############################
# LOGのヘッダーを読む関数
#############################
def readlog(filepath):
    log_order = [8,2,6,8,8,16,8,8,4,2,2,2,2,2]   # Log file structure
    log_use   = [1,0,0,1,0, 0,1,0,1,1,1,1,1,1]   # Bit for data will be used

    basename_wo_ext = os.path.splitext(os.path.basename(filepath))[0]  # Get hash characters
    base_name=(Path(filepath).name)
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
