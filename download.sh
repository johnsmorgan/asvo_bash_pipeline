index=$1
obsid=$2
if giant-squid submit-conv ${obsid} --wait -p timeres=0.5,freqres=160,edgewidth=160; then
	ssh garrawarla "/astro/mwasci/awaszewski/project/start.sh ${obsid}"
else
	echo ${obsid} ${index} >> failed.txt
fi
