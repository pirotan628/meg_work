#!/bin/bash
result='test.csv'  # Please change name to you preferred
rm ${result}       # Remove file if exists.
touch ${result}    # Make empty file

for file in $(find . -type f -name '*LOG'); do  # find: Sarch *.LOG file from all files
 
        dd if=${file} of=./tmp_hdr.txt bs=1 skip=0 count=8
        dd if=${file} of=./tmp_id.txt bs=1 skip=48 count=8
        dd if=${file} of=./tmp_yr.txt bs=1 skip=64 count=4
        dd if=${file} of=./tmp_mt.txt bs=1 skip=68 count=2
        dd if=${file} of=./tmp_dy.txt bs=1 skip=70 count=2
        dd if=${file} of=./tmp_hr.txt bs=1 skip=72 count=2
        dd if=${file} of=./tmp_min.txt bs=1 skip=74 count=2
        dd if=${file} of=./tmp_sec.txt bs=1 skip=76 count=2

	hdr=`cat tmp_hdr.txt`
	id=`cat tmp_id.txt`
	yr=`cat tmp_yr.txt`
	mt=`cat tmp_mt.txt`
	dy=`cat tmp_dy.txt`
	hr=`cat tmp_hr.txt`
	min=`cat tmp_min.txt`
	sec=`cat tmp_sec.txt`
        bn=`basename ${file}`

        hs="${bn%.*}"
        fdir="${file%/*}"
        tmp1="${fdir##*OR}"
        tmp2="${tmp1%/*}"
        orid=OR${tmp2}

        echo $orid, $yr$mt$dy ,$yr-$mt-$dy $hr:$min:$sec, $hs, $id, $hdr >> ${result}

done

cat ${result} | sed -e s'/\/NKT//'g | sed -e s'/\/EEG2100//'g | sed -e s'/\/EEG1100//'g > ck_result.csv

sort_result='test_sort.csv'  # This file will be used by "chdate.py"
#sort -k1,2 ${result} > ${sort_result}
sort -k1,2 ck_result.csv > ${sort_result}

rm tmp_*.txt