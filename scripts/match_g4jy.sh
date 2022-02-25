#!/usr/bin/env bash
set -euo pipefail

obsid=$1

# Change to directory where data is stored
data_dir="/data/awaszewski/project/obsids_109/"

f=${data_dir}/$obsid/${obsid}_out_comp.vot

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
