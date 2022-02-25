#!/bin/bash

set -euxo pipefail

obsid=$1
asvo=$2
DB_dir=$3
data_dir=$4
garra_dir=$5

if [ -z "$obsid" ] | [ -z "$asvo" ]; then
	echo "ERROR Observation ID or ASVO Job ID were not passed correctly, job has not been submitted to SLURM scheduler"
else
	# Generate slurm job 
	python3 ${garra_dir}/slurm_job_gen.py -o ${obsid} -c 38 -a ${asvo} --db_dir ${DB_dir} --data_dir ${data_dir} --garra_dir ${garra_dir}

	# Queue the job on Garrawarla
	sbatch ${garra_dir}/currently_running/${obsid}-job.sh
fi
