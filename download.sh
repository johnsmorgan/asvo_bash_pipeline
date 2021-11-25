set -euxo pipefail
index=$1
obsid=$2
if giant-squid submit-conv ${obsid} --wait -p timeres=0.5,freqres=160,edgewidth=160; then
	if ssh garrawarla "/astro/mwasci/awaszewski/project/start.sh ${obsid}"; then
		echo ${obsid} ${index} >> complete.txt
	else
		echo ${obsid} ${index} >> ssh_failed.txt
else
	echo ${obsid} ${index} >> giant_squid_failed.txt
fi
