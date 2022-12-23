#  使い方：
#  python3 ap_readcsv.py [csvファイル名]
#  [csvファイル名]は"data/Nanashi.csv"とかパス入りもOK
# Nanashi_1-line.csv が変換後

import sys
import csv
#import io
import pandas as pd
import os


#-----------------------------------
# wavファイル名から余分な文字消去する関数
def GetCodeFromWav(wavname):
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

rows_L = []  # 奇数行用のリスト（左側）
rows_R = []  # 偶数行用のリスト（右側）
i = 0
with open(filename, "r", encoding='shift_jis') as f:
    reader = csv.reader(f)
    for row in reader:
        if row != []:
            i += 1
            if (i % 2) > 0:  # 偶数行
                rows_L.append(row)
            else:            # 奇数行
                rows_R.append(row)

f.close()

#print(rows_L)
#print(rows_R)

# 2次元配列の結合
row_ex = []
rows = []
for j in range(len(rows_L)):
   row_ex = rows_L[j]
   row_ex.extend(rows_R[j])
   rows.append(row_ex)

# pandas DataFrameへ変換
df = pd.DataFrame(rows)
df = df.drop(columns=[0,2,3])

# wavファイル名から余分な文字消去
df.loc[:,1] = df.loc[:,1].apply(GetCodeFromWav)

# シャープの文字がバラバラ!!なのを統一する
df.loc[:,4] = df.loc[:,4].replace("♯","#", regex=True)

# 正答率計算
# 正当判定 (CAR; Correct answer rate)
for n in range(len(df.index)):
     df.loc[n,6]=CheckAns(df.loc[n,1], df.loc[n,4])

df.loc[:,6] = df.loc[:,6].astype(float)  #文字型を数値型に
car = df.loc[:,6].mean() * 100
print("Correct answer rate: ", car)

# 平均解答時間の算出
df.loc[:,5] = df.loc[:,5].astype(float)  #文字型を数値型に
avg_time = df.loc[:,5].mean()
print("ANS avg. time: ",avg_time)


print(df)

# CSVファイルに書き出し
ofilename = basename + "_1-line.csv"
df.to_csv(ofilename, index=False)

# 最終行に平均解答時間と正答率を追記
f = open(ofilename,'a')
f.write(",,"+str(avg_time)+","+str(car))
f.close()
