#!/usr/bin/env python3
import os, datetime
import sqlite3 as lite
from optparse import OptionParser
from datetime import datetime

# Initialise where database file is stored (in .bashrc)
DB_FILE = os.environ['DB_FILE']

# Information required to update database
parser = OptionParser()
parser.add_option("-o", "--obsid", dest="obsid", default=None, type=int, help="Observation's ID")
parser.add_option("-s", "--status", dest="status", default="Failed", type=str, help="Status of observation in the pipeline (eg. completed, failed, etc.)")

opts, args = parser.parse_args()

# At least the observation that is to be updated needs to be known
if opts.obsid is None:
    parser.error("Obsid must be set")

# Time when processing of the observation has finished
end_time = datetime.now()

obsid=int(opts.obsid)

con = lite.connect(DB_FILE)
with con:
    cur = con.cursor()
    if opts.status == "Failed":
        cur.execute("UPDATE Log SET Ended=?, Status=? WHERE Obsid=?", (end_time, opts.status, obsid))
    else:
        query = "SELECT Started FROM Log WHERE Obsid=%d" % (obsid)
        #cur.execute("SELECT Started FROM Log WHERE Obsid=?", (opts.obsid))
        cur.execute(query)
        start_time = cur.fetchone()[0]
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f')
        time_diff = end_time - start_time
        diff = time_diff.total_seconds()
        cur.execute("UPDATE Log SET Ended=?, Time=?, Status=? WHERE Obsid=?", (end_time, diff, opts.status, obsid))
