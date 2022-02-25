set -euxo pipefail

#Initialise database where pipeline information will be stored
DB_dir="/data/awaszewski/EoR_scin_pipeline/db/"

export DB_FILE=${DB_dir}log.sqlite
python3 ${DB_dir}/init_db.py

#Run through all obsids, running n_parallel at any one time
n_parallel=10
cat obsids | xargs -P $n_parallel -d $'\n' -n 1 bash ./scripts/run_pipeline.sh $DB_dir
