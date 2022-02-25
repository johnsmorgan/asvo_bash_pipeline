#!/bin/bash

set -euxo pipefail

obsid=$1
asvo=$2

# Change to directory where pipeline is being run
pipeline_dir="/astro/mwasci/awaszewski/EoR_scin_pipeline/"

if [ -z "$obsid" ] | [ -z "$asvo" ]; then
	echo "ERROR Too few arguments were given, job was not submitted to Garrawarla"
else
	# Generate slurm job 
	python3 ${pipeline_dir}slurm_job_gen.py -o ${obsid} -c 38 -a ${asvo}

	# Queue the job on Garrawarla
	sbatch ${pipeline_dir}currently_running/${obsid}-job.sh
fi
