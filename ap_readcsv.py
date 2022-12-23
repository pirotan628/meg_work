import sys
import csv
#import io
import pandas as pd
import os

filename = sys.argv[1]
basename = os.path.splitext(os.path.basename(filename))[0]
print(basename)

rows_L = []  # 奇数行用のリスト（左側）()
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
print(df)

ofilename = basename + "_1-line.csv"
df.to_csv(ofilename)

df.loc[:,5] = df.loc[:,5].astype(float)
avg_time = df.loc[:,5].mean()

print("ANS avg. time: ",avg_time)