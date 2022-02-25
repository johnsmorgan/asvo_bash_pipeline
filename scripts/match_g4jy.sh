#!/usr/bin/env bash
set -euo pipefail

dir=$1

# Get obsid from directory string
IFS='/'
read -a strarr <<< "$dir"
obsid=${strarr[-1]}

if [[ ${#obsid} -ne 10 ]]; then
	echo ERROR Observation ID is incorrect
else
	if [ -d ${dir} ]; then
		f=${dir}/${obsid}_out_comp.vot

		topcat -stilts tmatch2 \
			in1=$f \
			in2=eor0_g4jy_ips.vot \
			values1="ra dec" \
			values2="centroid_RAJ2000 centroid_DEJ2000" \
			find="all" \
			join="all1" \
			matcher=sky \
			params=120 \
			ocmd="addcol snr peak_flux/local_rms" \
			ocmd="sort -down snr" \
			ocmd="head 50" \
			out=${f%.vot}_g4jy.vot
	else
		echo ERROR Data directory does not exist
	fi
fi
