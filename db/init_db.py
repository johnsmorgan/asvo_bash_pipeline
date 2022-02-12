import os
import sqlite3 as lite

try:
    DB_FILE = os.environ['DB_FILE']
except:
    print("ERROR: Environmental variable DB_FILE must be defined")

con = lite.connect(DB_FILE)
with con:
    cur = con.cursor()
    # Obsid - Observation ID (gps seconds)
    # ASVOJobID - ASVO Job ID
    # Submitted - time job was submitted to ASVO
    # Datadir - path to main data store
    # JobID - Slurm Job ID
    # Started - processing start time on Garrawarla
    # Ended - end time, NULL implies that the job is running or was recently terminated
    # Time - Run time in seconds
    # Status - Current status of observation in pipeline (eg, on asvo, processing, failed, completed)
    cur.execute("CREATE TABLE Log(Rownum integer primary key autoincrement, Obsid INT, ASVOJobID INT, Submitted date, Datadir TEXT, JobID INT, Started date, Ended date, Time INT, Status TEXT)")
