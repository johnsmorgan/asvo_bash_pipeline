#!/bin/bash
set -euox pipefail

obsid=$1

moment_image=/home/jmorgan/Working/imstack/imstack/moment_image.py
data_dir=/data/awaszewski/project/obsids_109

# Creation of individual moment images along with the moment image cube
echo ${obsid}
if [ -d ${data_dir}/${obsid} ]; then
	cd ${data_dir}/${obsid}
	mpirun -n 8 --oversubscribe --timestamp-output python ${moment_image} ${obsid}.hdf5 \
		--filter_lo --filter_hi --suffix=image
else
	echo ${obsid} does not exist
fi
