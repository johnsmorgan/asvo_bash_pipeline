#!/usr/bin/env python3

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--obsid", type=int, required=True,
                                        help="The observation ID")
parser.add_argument("-c", "--cpus", type=int, required=False, default=38,
                                        help="Number of CPUs to be used")
parser.add_argument("-a", "--asvo", type=int, required=True,
										help="ASVO Job ID")
args = parser.parse_args()

# Change to directory where database is stored (DB_FILE)
db_dir="/data/awaszewski/EoR_scin_pipeline/db/"
# Change to directory where pipeline is being controlled from
pipeline_dir="/astro/mwasci/awaszewski/EoR_scin_pipeline/"
# Change to directory where processed data is stored
data_dir="/data/awaszewski/project/obsids_109/"

obsnum = args.obsid
filename = f"{pipeline_dir}/currently_running/{obsnum}-job.sh"
f = open(filename,"w+")

def gen_slurm(obsid, cpus, asvo):
	string = f"""#!/bin/bash -l
#SBATCH --gres=tmp:250g
#SBATCH --nodes=1
#SBATCH --ntasks-per-node={cpus}
#SBATCH --cpus-per-task=1
#SBATCH --job-name={obsid}
#SBATCH --output=/astro/mwasci/awaszewski/EoR_scin_pipeline/currently_running/{obsid}-pipeline.out
#SBATCH --time=01:00:00
#SBATCH --partition=workq
#SBATCH --account=mwasci

set -exE

trap 'ssh mwa-solar "export DB_FILE={db_dir}log.sqlite; python3 {db_dir}db_end_log.py -o {obsid} -s Failed"' ERR

# Move to the temporary working directory on the NVMe
cd /nvmetmp

# Load relevant modules
module use /pawsey/mwa/software/python3/modulefiles
module use /pawsey/mwa_sles12sp5/modulefiles/python
module load giant-squid wsclean mwa-reduce
module load python aocalpy scipy astropy h5py

# Update database to set observation to processing on garrawarla
ssh mwa-solar "export DB_FILE={db_dir}log.sqlite; python3 {db_dir}db_update_log.py -o {obsid} -j $SLURM_JOB_ID"

# Locate measurement set off of ASVO
ms=/astro/mwasci/asvo/{asvo}/{obsid}.ms

# Copy model.txt file from Magnus
scp hpc-data:/group/mwasci/jmorgan/qadb_models/{obsid}_model.txt ./

# Create stats file
taql -m 100 "select ctod(TIME), gsum(ntrue(FLAG[,::3])), gmean(WEIGHT_SPECTRUM[,::3]), gsum(ntrue(amplitude(DATA[,::3])==0.0)) from $ms where ANTENNA1 != ANTENNA2 groupby TIME" > {obsid}_stats.txt

# Calibration of snapshot images to use in phase plots
calibrate -minuv 130 -maxuv 1300 -j {cpus} -t 1 -m {obsid}_model.txt $ms {obsid}_multi.bin

# Find bad tiles
scp hpc-data:{pipeline_dir}flagbadtiles.py ./
flagtiles=$(python3 ./flagbadtiles.py {obsid} $ms)

# Flag bad tiles
$flagtiles

# Calibration of full image to use in imaging and analysis
calibrate -minuv 130 -maxuv 1300 -j {cpus} -m {obsid}_model.txt $ms {obsid}.bin

# Apply solutions of full calibration
applysolutions $ms {obsid}.bin -nocopy

# Image full standard image
size=2400
minuv_l=5
niter=12000
automask=3
autothresh=2
scale=1amin
nmiter=5
mgain=0.8
wsclean -j {cpus} -name {obsid} -pol xx,yy -size $size $size -join-polarizations -minuv-l $minuv_l -weight briggs 1.0 -niter $niter -auto-mask $automask -auto-threshold $autothresh -nmiter $nmiter -scale $scale -log-time -mgain $mgain $ms

# Flag outer tiles
flagantennae $ms 0 7 8 9 10 15 16 17 29 31 32 33 34 35 36 37 38 39 40 48 49 50 51 52 53 54 55 56 57 62 63 64 65 66 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106 107 108 109 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124 125 126 127

# Image snapshot images
interval_start=2
interval_stop=53
intervals_out=$((interval_stop-interval_start))
wsclean -j {cpus} -name {obsid} -subtract-model -pol xx,yy -size $size $size -join-polarizations -minuv-l $minuv_l -weight briggs 1.0 -nwlayers 18 -niter $niter -auto-mask $automask -auto-threshold $autothresh -scale $scale -log-time -no-reorder -no-update-model-required -interval $interval_start $interval_stop -intervals-out $intervals_out $ms

# Make hdf5 file
scp hpc-data:{pipeline_dir}hdf5/*.py ./
scp mwa-solar:{data_dir}{obsid}/*.metafits ./
python3 ./make_imstack.py -n 50 --start=0 --step=1 --suffixes=image --outfile={obsid}.hdf5 --skip_beam --allow_missing {obsid}
python3 ./lookup_beam_imstack.py {obsid}.hdf5 {obsid}.metafits 109-132 --beam_path {pipeline_dir}hdf5/gleam_xx_yy.hdf5
python3 ./add_continuum.py {obsid}.hdf5 {obsid} image

# Copy back any relevant data
rsync -a *stats.txt mwa-solar:{data_dir}{obsid}/
rsync -a *.bin mwa-solar:{data_dir}{obsid}/
rsync -a *.hdf5 mwa-solar:{data_dir}{obsid}/
rsync -a {obsid}-XX-image.fits mwa-solar:{data_dir}{obsid}/
rsync -a {obsid}-YY-image.fits mwa-solar:{data_dir}{obsid}/
rsync -a {obsid}-XX-model.fits mwa-solar:{data_dir}{obsid}/
rsync -a {obsid}-YY-model.fits mwa-solar:{data_dir}{obsid}/

# Update database to show that observation has finished processing
ssh mwa-solar "export DB_FILE={db_dir}log.sqlite; python3 {db_dir}db_end_log.py -o {obsid} -s Completed" 

# Clean up temp working directory
rm -r *{obsid}*
"""
	return string

f.write(gen_slurm(args.obsid, args.cpus, args.asvo))
f.close()

