obsid=$1
index=$2
echo ${obsid}
if giant-squid submit-conv ${obsid} --wait -p timeres=0.5,freqres=160,edgewidth=160; then
	if ssh garrawarla "bash /astro/mwasci/awaszewski/project/start.sh ${obsid}"; then
		echo ${obsid} ${index} >> ssh_succeed.txt
	else
		echo ${obsid} ${index} >> ssh_failed.txt
	fi
else
	echo ${obsid} ${index} >> giant_squid_failed.txt
fi
