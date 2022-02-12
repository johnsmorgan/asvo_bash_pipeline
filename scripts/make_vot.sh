#!/bin/bash

set -euxo pipefail

obsid=$1
data_dir=/data/awaszewski/project/obsids_109

# Move to directory where processed data is stored
cd $data_dir/$obsid
	
# Run source finding 
BANE ${obsid}-XX-image.fits
aegean --autoload ${obsid}-XX-image.fits --table ${obsid}_out.vot
