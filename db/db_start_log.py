#!/usr/bin/env python3
import os, datetime
import sqlite3 as lite
from optparse import OptionParser

# Initialise where database file is stored (in .bashrc)
DB_FILE = os.environ['DB_FILE']

# Information required to update database
parser = OptionParser()
parser.add_option("-o",  "--obsid", dest="obsid", default=None, type=int, 
                        help="Observation's ID")
parser.add_option("-a", "--asvojobid", dest="asvojobid", default=None, type=int,
                        help="ASVO Job ID")

opts, args = parser.parse_args()

# At least the observation that is to be updated must be known
if opts.obsid is None:
    parser.error("Obsid must be set")

# Time when processing of observation on ASVO began
current_time = datetime.datetime.now()

con = lite.connect(DB_FILE)
with con:
    cur = con.cursor()
    cur.execute("UPDATE Log SET ASVOJobID=?, Submitted=?, Status=? WHERE Obsid=?", (opts.asvojobid, current_time, "Processing on ASVO", opts.obsid))
