n_parallel=10
cat obsids | xargs -P $n_cpus -d $'\n' -n 1 ./download.sh
