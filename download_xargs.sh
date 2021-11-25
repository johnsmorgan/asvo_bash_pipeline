set -euxo pipefail
n_parallel=10
cat obsids_test | xargs -P $n_parallel -d $'\n' -n 1 ./download.sh
