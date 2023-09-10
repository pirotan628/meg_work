import glob   # ファイル検索する
import os     # OSの機能使う
import shutil

dir_org = "sampledata-before"
dir_edf_root = "sampledata-edf"
dir_fixed_root = "sampledata-fixed"

# fir_org に dir_edf + dir_fixed_bin からファイルを集める
# orgのbin/csvのファイル名を変更して残す?->消す

harudirs = glob.glob(os.path.join(dir_org,"*"))
osep = os.sep
sep = "_"
header = "raw_"
footer = "_00000"
exts = [".bin", ".csv", ".edf"]

for dirs in harudirs:
    dst = dirs.split(osep)[-1] # Hxxxx_xx_yyyymmddtttttt
    ymd = dst.split(sep)[2] # yyyymmddtttttt

    fn_base = header + ymd + footer
    bin_fn = os.path.join(dir_fixed_root, fn_base + exts[0])
    csv_fn = os.path.join(dir_fixed_root, fn_base + exts[1])
    edf_fn = os.path.join(dir_edf_root,fn_base,fn_base + exts[2])
    
    for source in [bin_fn,csv_fn,edf_fn]:
        if os.path.isfile(source):
            print ("copy", source, "->", dirs)
            fn_base = source.split(osep)[-1]
            org_fn = os.path.join(dirs,fn_base)  #コピー先のファイル(ノイズあり想定)
            if os.path.isfile(org_fn): #コピー先ファイル存在確認
                #コピー先のファイルを残す場合
#                shutil.move(os.path.join(dirs,fn_base),os.path.join(dirs,fn_base+".org"))
#                print("renamed ", fn_base, "->" , fn_base+".org")
                #コピー先のファイルを消す場合
                os.remove(org_fn)
                print("Removed original", org_fn)
                shutil.copyfile(source, org_fn)
            else:    #コピー先のファイルが無い場合はコピーするのみ
                shutil.copyfile(source, org_fn)
        else:  #コピー元のファイルが無い場合はコピーできない
            print(source, "is not exists.")
