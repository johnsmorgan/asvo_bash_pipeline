obsid=$1
index=$2
echo ${obsid}

set -exE

if [ -z "$obsid" ]; then
	echo "ERROR Observation ID has not been passed correctly"
else
	# Set all database commands
	DB_dir="/data/awaszewski/EoR_scin_pipeline/db/"
	DB_FILE="${DB_dir}log.sqlite"
	DB_add="${DB_dir}db_add_log.py"
	DB_start="${DB_dir}db_start_log.py"
	DB_view="${DB_dir}db_view_log.py"
	DB_update="${DB_dir}db_update_log.py"
	DB_end="${DB_dir}db_end_log.py"

	# Change to directory where data needs to be stored at the end of the pipeline
	data_dir="/data/awaszewski/project/obsids_109/${obsid}/"
	# Change to directory on Garrawarla where second half of pipeline will run
	garra_dir="/astro/mwasci/awaszewski/EoR_scin_pipeline/"
	# Change to directory where pipeline is being controlled from
	pipeline_dir="/data/awaszewski/EoR_scin_pipeline/"

	# Set all pipeline commands
	scripts="${pipeline_dir}/scripts/"
	moment="${scripts}/moment_image.sh"
	vot="${scripts}/make_vot.sh"
	match="${scripts}/match_g4jy.sh"

	# Add current observation to database
	python3 $DB_add -o ${obsid} -d ${data_dir}

	# Submit job to ASVO, pipeline will wait until job is ready to be downloaded
	if giant-squid submit-conv ${obsid} --wait -p conversion=ms,timeres=0.5,freqres=160,edgewidth=160 -d astro -e 2; then
		
		# Find ASVO Job ID
		giant-squid list > asvo_${obsid}
		asvojob=$(grep ${obsid} asvo_${obsid} | awk '{print $2}')
		rm asvo_${obsid}*

		# Set database for observation to processed on ASVO
		python3 $DB_start -o ${obsid} -a ${asvojob}

		# Start processing job on garrawarla
		if ssh garrawarla "bash ${garra_dir}/start.sh ${obsid} ${asvojob}"; then
			echo ${obsid} ${index} >> ssh_succeed.txt
			
			# Continuously check database to see if observation has finished running
			running=0
			while [ ${running} -eq 0 ]
			do
				output=$(python3 $DB_view -o ${obsid})
				if [[ "$output" == *"Processing"* ]]; then
					running=0
				elif [[ "$output" == *"Processed on ASVO"* ]]; then
					running=0
				else
					running=1
				fi
			done
		
			if [[ "${output}" == *"Failed"* ]]; then
				echo ${obsid} ${index} >> processing_failed.txt
			else	
				# Final clean up of /astro, including measurement set
				scp hpc-data:${garra_dir}currently_running/${obsid}* $data_dir
				ssh garrawarla "cd ${garra_dir}currently_running/; rm ${obsid}*; cd /astro/mwasci/asvo/${asvojob}/; rm ${obsid}.ms"
			
				# Moment images
				bash $moment ${obsid}

				# Source finding
				bash $vot ${obsid}

				# Cross-match with G4Jy survey
				bash $match ${obsid}

				echo ${obsid} ${index} >> processing_complete.txt
			fi
		else
			# If communication with garrawarla fails pipeline will be terminated
			python3 $DB_end -o ${obsid} -s Failed
			echo ${obsid} ${index} >> garrawarla_failed.txt
		fi
	else
		# If the job is unable to be submitted or fails during processing pipeline will be terminated
		python3 $DB_end -o ${obsid} -s Failed
		echo ${obsid} ${index} >> asvo_failed.txt
	fi
fi
