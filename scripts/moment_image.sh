#!/bin/bash
set -euox pipefail

dir=$1

# Get obsid from directory string
IFS='/'
read -a strarr <<< "$dir"
obsid=${strarr[-1]}

moment_image=/home/jmorgan/Working/imstack/imstack/moment_image.py

# Creation of individual moment images along with the moment image cube
if [[ ${#obsid} -ne 10 ]]; then
	echo ERROR Observation ID incorrect
else
	echo ${obsid}
	if [ -d ${dir} ]; then
		cd ${dir}
		mpirun -n 8 --oversubscribe --timestamp-output python ${moment_image} ${obsid}.hdf5 \
			--filter_lo --filter_hi --suffix=image
	else
		echo ERROR Data directory does not exist
	fi
fi
