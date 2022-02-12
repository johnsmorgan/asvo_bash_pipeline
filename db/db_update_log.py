#!/usr/bin/env python3
import os, datetime
import sqlite3 as lite
from optparse import OptionParser

# Initialise where database file is stored (in .bashrc)
DB_FILE = os.environ['DB_FILE']

# Information required to update database
parser = OptionParser()
parser.add_option("-o", "--obsid", dest="obsid", default=None, type=int,
                    help="Observation's ID")
parser.add_option("-j", "--jobid", dest="jobid", default=None, type=int,
                    help="SLURM Job ID")
parser.add_option("-s", "--status", dest="status", default=None, type=str,
                    help="Status that the user would like to place the observation under")
opts, args = parser.parse_args()

# At least the observation that is to be updated needs to be known
if opts.obsid is None:
    parser.error("Obsid must be set")

# Time that processing of observation started on Garrawarla
current_time = datetime.datetime.now()

con = lite.connect(DB_FILE)
with con:
    cur = con.cursor()
    if opts.jobid is not None:
        cur.execute("UPDATE Log SET JobID=?, Started=?, Status=? WHERE Obsid=?", (opts.jobid, current_time, "Processing", opts.obsid))
    if opts.status is not None:
        cur.execute("UPDATE Log SET Status=? WHERE Obsid=?", (opts.status, opts.obsid))
