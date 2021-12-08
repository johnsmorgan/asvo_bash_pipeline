set -euxo pipefail

#Initialise database where completion information will be stored
ssh garrawarla "cd /astro/mwasci/awaszewski/project; export DB_FILE=/astro/mwasci/awaszewski/project/log.sqlite; python3 init_db.py"

#Run through all obsids, running 10 at any one time
n_parallel=10
cat obsids_test | xargs -P $n_parallel -d $'\n' -n 1 ./download.sh
