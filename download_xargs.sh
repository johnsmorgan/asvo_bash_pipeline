n_parallel=10
cat obsids | xargs -P $n_parallel -d $'\n' -n 1 ./download.sh
