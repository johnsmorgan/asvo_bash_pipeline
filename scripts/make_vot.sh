#!/bin/bash

set -euxo pipefail

dir=$1

# Get obsid from directory string
IFS='/'
read -a strarr <<< "$dir"
obsid=${strarr[-1]}

# Move into data directory
if [[ ${#obsid} -ne 10 ]]; then
	echo ERROR Observation ID is incorrect
else
	if [ -d ${dir} ]; then
		cd $dir

		# Run source finding 
		BANE ${obsid}-XX-image.fits
		aegean --autoload ${obsid}-XX-image.fits --table ${obsid}_out.vot
	else
		echo ERROR Data directory does not exist
	fi
fi
