# asvo-bash-pipeline

The goal of this pipeline is to process MWA EoR Phase I data for the study of ionospheric scintillation, although it can be made applicable to other MWA datasets. With the simple orchestration of [ASVO](https://asvo.mwatelescope.org/) downloads using bash, xargs, and [giant-squid](https://gitlab.com/chjordan/giant-squid#readme), a user-inputed list of MWA observations are downloaded off of ASVO and processed. This pipeline has been written for the Pawsey Garrawarla system, as it makes use of the updated ASVO delivery system straight onto ```/astro```.

## Pipeline Description
The pipeline is divided into two major sections; the first section runs on any machine which controls the pipeline and does some post-imaging work, while the second section runs on the Pawsey Garrawarla system and handles the majority of the observation processing and imaging. 

The pipeline is structured in such a way that allows for freedom of how many observations are being processed at any one time, giving the user to control how much of shared ASVO and SLURM resources they are using. This can also be useful during times of peak resource use, where it may be beneficial to only process a few observations at a time. To manage this aspect, the user is able to change the variable n_parallel in the main pipeline script pipeline_control.sh to any number they see fit. By using xargs to handle this parallelisation portion of the pipeline, even if an observation fails to be processed or imaged, the pipeline will not halt, but rather note the failed observation and begin processing the next observation in the list.

During the processing of an observation, a job will first be submitted to ASVO, specifying it to be downloaded straight to ```/astro```. The pipeline will wait until the ASVO job has completed and the necessary data is available in the ASVO directory (```/astro/mwasci/asvo/```). The imaging job script will then be created, and submitted to the SLURM scheduler. Once again, the pipeline will wait until the observation has finished processing on Garrawarla before proceeding. As the SLURM job finishes, all relevant data (images, job and out files, etc) will be transferred back to the machine where the pipline was initailised, leaving no data on ```/astro```, therefore limiting strain on shared resources.

The pipeline takes only one input, a list of MWA observations that are to be processed passed in a single text file ```obsids```, while giving multiple outputs;
- Calibration solutions (.bin and _multi.bin)
- Deep continuum images for both polarisations with models (-XX-model.fits, -YY-model.fits, -XX-image.fits, -YY-image.fits)
- Variability hdf5 image cube (.hdf5)
- Moment images (_moment1.fits, _moment2.fits, _moment3.fits, _moment4.fits, _moments.hdf5)
- Source-found and cross-matched tables (_out_comp.vot, _out_comp_g4jy.vot)

All information about the observation throughout the duration of the pipeline is stored in the database. At any time, with the pipeline running in the background, the user is able to view the current database to view the status of all or particular observations using ```db/db_view_log.py```. Once the pipeline is complete, it is still possible to access the database to view what has been previously processed. 

## Structure
Code directory:
- db: contains the python scripts that are used to create, manage, and navigate the database used to manage processing observations
- scripts: contains the bash scripts that are used in running the pipeline and final steps in post-imaging
- garrawarla: contains the files that need to exist on /astro

Base path:
- obsids: text file of the list of MWA observations that are to be processed
- pipline_control.sh: bash script that starts and controls the pipeline, running a number (default is 10) observations at any one time

## Installation and Dependencies
### Database Initialisation
Add the following to your ```.bashrc```
```
export DB_FILE=~/path/to/log.sqlite
export PATH=$PATH:[path-to]/db/
```
Once the pipeline has been started, the database file ```log.sqlite``` will be automatically created

### Paths and Directories
There are a number of scripts that rely on paths to directories being changed. These scripts are listed below, and any directory that needs to be changed will be near the top of the file with a comment explaining where each path should point too. 
- ```pipeline_control.sh``` (in base path)
  * DB_dir = /path/to/db (same as $PATH in .bashrc)
- ```run_pipeline.sh```
  * data_dir = /path/to/processed/data/storage (directory where all observation directories will be)
  * garra_dir = /path/to/pipeline/on/garrawarla (contents of garrawarla folder go here)
  * pipeline_dir = /path/to/pipeline/directory (where this repo is cloned too)

In the ```data_dir```, every observation will require it's own directory. In each observation directory both a {obsid}.metafits file and {obsid}_model.txt need to exist

### /astro Preparation
Although the whole pipeline does not need to exist on a supercomputer to run, a portion of it does. The garrawarla folder contains all the scripts that must be on ```/astro```, where the garra_dir specifies. Therefore to prep the garra_dir
- Move garrawarla folder to user-specified place on ```/astro``` (```garra_dir```)
- Copy over gleam_xx_yy.hdf5 to ```garra_dir/hdf5```

### Other Dependencies
These are the external dependencies that are required to run this pipeline. For installation instructions, please follow the respective links.
- [giant-squid](https://github.com/MWATelescope/giant-squid)
- [Aegean](https://github.com/PaulHancock/Aegean)

## Running the Pipeline
Before running the pipeline, first make sure the text file obsids is populated with all observations that are to be processed with each on a new line. Then all that is required is to run ```pipeline_control.sh``` in ```pipeline_dir```.

## Detailed script descriptions
