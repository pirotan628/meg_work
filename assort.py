import glob   # ファイル操作する
import os     # OSの機能使う
import struct #
from datetime import timedelta  # 日付時刻データ扱う
import re     # 正規表現扱う（条件指定など）
import shutil #
from pathlib import Path
import sys

#############################
# 新しいファイルだけコピーする関数
#############################
def copy_new(source, destination, sentence):
    os.makedirs(os.path.dirname(destination), exist_ok=True)         # Make directories for new files
        
    if os.path.isfile(source) and (not os.path.exists(destination)):    # Process if it is a file (except directory) and new.
        shutil.copy2(source, destination)                               # Copy file
        sys.stderr.write((sentence + " copied."+'\n'))
    else:
        sys.stderr.write((sentence + " passed."+'\n'))

##############################
#  コピー先のディレクトリ作成
##############################
current_path = os.getcwd()
parent_path = os.path.dirname(current_path)
dist_path = os.path.join(parent_path, "ASSORT")

if os.path.exists(dist_path):
    sys.stderr.write((dist_path + " is already exists."+'\n'))
else:
    os.mkdir(dist_path)
    sys.stderr.write(("Created " + dist_path+'\n'))


###############################
# Read file
###############################
#osep = os.sep  # OSごとに異なるPATHの区切り文字を取得
# Windows の場合は"¥"か"\"が得られる
# Mac / Linuxだと"/"

orids = []  # 変数宣言（予約）
# orids には"OR"で始まる（下で定義）フォルダのリストが格納される
# @@@@@@ ここは変える必要あり
orids = glob.glob("OR*")  # Get parent folder names (OR-**) represent trialists.
# @@@@@@

#探す拡張子リスト
#extlist = ["eeg", "elp", "mul", "log", "evt"]  # 大文字小文字問わず
extlist = ['.eeg', '.elp', '.mul', '.log', '.evt']  # 必要な拡張子リスト、小文字
ignorelist = ['.ptn', '.11d', '.21e', '.cmt', '.cn2', '.eg2', '.eg_', '.pnt']   # 除外リスト


######################################
# len(orids)はORのつくフォルダの数
for n_orid in range(len(orids)):  # Process each trialist individually
    orid = orids[n_orid] #n_orid番目の"OR"フォルダ名
    # ["ORxxxx" + "¥" + "**" + "¥" + "*.LOG/evt/..."]
    # ORxxxxというフォルダの下の任意のフォルダ(**)の下のファイルを探す(拡張子リスト)
    # recursive=True 下層のフォルダまで繰り返す
    path_name = os.path.join(orid, "**", "*.*")
    all_file_list = glob.glob(path_name, recursive=True)  # All file list in OR*

    session_list = []
    base_stems = []
    base_names = []
    proc_path = []
    for file_path in all_file_list:
         root, extraw = os.path.splitext(file_path)  #ファイル名（パス有り）と拡張子の取得
         ext = extraw.lower()                  #除外判定用の拡張子の小文字化
         if not (ext in ignorelist):           #除外リスト以外を処理する
             base_stem=(Path(file_path).stem)  #拡張子なし名前（パスなし＝1回の測定の名前
             base_name=(Path(file_path).name)  #拡張子あり名前（パスなし）

             base_stems.append(base_stem)         #拡張子なし名前のリストに追加
             base_names.append(base_name.lower()) #ファイル名の小文字化とファイル名リストに追加
             proc_path.append(file_path)          #処理するファイル（パスあり）リストに追加

    session_list = list(set(base_stems))  # 1回の測定の名前のリスト(FJ**, 整理されていれば OR-NNN-NN-YYYYmmdd)
    file_num=0
    for n in session_list:
        exist_list = []                # 存在リスト、初期値＝空
        absent_list = list(extlist)    # 欠損リスト、初期値＝全て
        for e in extlist:
            candidate = n + e          # 存在して欲しい候補名
            if candidate.lower() in base_names: # 存在した場合
                exist_list.append(e)   # 存在リストに拡張子を追加
                absent_list.remove(e)  # 欠損リストから該当の拡張子を削除
                file_num = file_num + 1 # ファイル数のカウント

        sentence=" ".join([orid, n, "--> Exist:",str(exist_list), "Absent:", str(absent_list)])
        print(sentence)

#############################
# Copy files
#############################

    i=0
    for org in proc_path:   #処理するファイル（パスあり）リスト
        i = i + 1
        progress = (100 * i / file_num)             # Calc progress [%]
        org_name = Path(org).name                   # コピー元
        dist = os.path.join(dist_path, orid, org_name)  # コピー先

        sentence= org + " -> " + dist + " [" + str(i) +"/"+ str(file_num) +" ("+format(progress, '5.1f')+"%)" + "]"
        copy_new(org, dist, sentence)
