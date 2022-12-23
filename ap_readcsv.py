#  使い方：
#  python3 ap_readcsv.py [csvファイル名]
#  [csvファイル名]は"data/Nanashi.csv"とかパス入りもOK
# Nanashi_1-line.csv が変換後

import sys
import csv
import pandas as pd
import os

#-----------------------------------
# wavファイル名から余分な文字消去する関数
def GetCodeFromWav(wavname):
     if wavname == "":
        return wavname

     raw = wavname.replace(".wav", "") #拡張子消す
     raw = raw[:-1]  #最後尾は数字なので消す
     token = raw.split('_')  #"_"で文字列を分割
     code = token[1]  #"_"で区切られた後ろだけ抽出
#     print(code)
     return code
#-----------------------------------

#-----------------------------------
# 回答に正解が含まれるか判定する関数
def CheckAns(sound,ans):
     if sound in ans:
         result = 1
     else:
         result = 0

     return result
#-----------------------------------

filename = sys.argv[1]
basename = os.path.splitext(os.path.basename(filename))[0]
print(basename)

rows_play = []   # play用のリスト（左側）
rows_click = []  # click用のリスト（右側）
play = False

row_click_null = ["no-click","",'nan']  #ダミーの不正解クリック

with open(filename, "r", encoding='shift_jis') as f:
    reader = csv.reader(f)  #CSVを読んでリストのリストを得る[[row='a','b',,,'z'],[row],[row],,,[row]]
    for row in reader:  #1行ずつCSVを処理する
        if row != []:  #空白行は無視
            if row[0]=="play":    #play行の処理
                 rows_play.append(row)   #play内容を追記
                 if play==True: #一個前がplayだった場合（clickされてない）
                    rows_click.append(row_click_null) #ダミー（不正解クリック）を追記
                 play = True  #playされたフラグ
            elif row[0]=="click": #click行の処理
                 if play==False:  #1個前が再生されてない（連続クリック）場合
                    rows_click.pop(-1)  #前回を消す
                 rows_click.append(row) #最新のクリック結果を追記
                 play = False   #clickのフラグ（1-playの終了）

f.close()

# 2次元配列の結合
rows = rows_play
for j in range(len(rows)):
    rows[j].extend(rows_click[j])

# pandas DataFrameへ変換
df = pd.DataFrame(rows)
df = df.drop(columns=[0,2,3])

# wavファイル名から余分な文字消去
df.loc[:,1] = df.loc[:,1].apply(GetCodeFromWav)

# シャープの文字がバラバラ!!なのを統一する
df.loc[:,4] = df.loc[:,4].replace("♯","#", regex=True)

# 正答率計算
for n in range(len(df.index)): #正答判定 (CAR; Correct answer rate)
     df.loc[n,6]=CheckAns(df.loc[n,1], df.loc[n,4])

df.loc[:,6] = df.loc[:,6].astype(float)  #文字型を数値型に
car = df.loc[:,6].mean() * 100   #正答率(%)

# 平均解答時間の算出
df.loc[:,5] = df.loc[:,5].astype(float)  #文字型を数値型に
avg_time = df.loc[:,5].mean()

print(df)
print("Correct answer rate: ", car)
print("ANS avg. time: ",avg_time)

# CSVファイルに書き出し
ofilename = basename + "_1-line.csv"
df.to_csv(ofilename, index=False)

# 最終行に平均解答時間と正答率を追記
f = open(ofilename,'a')
f.write(",,"+str(avg_time)+","+str(car))
f.close()
