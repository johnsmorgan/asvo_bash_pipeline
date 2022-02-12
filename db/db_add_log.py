#!/usr/bin/env python3
import os, datetime, logging
import sqlite3 as lite
from optparse import OptionParser

# Initialise where database file is stored (in .bashrc)
DB_FILE = os.environ['DB_FILE']

# Information required to update database
parser = OptionParser()
parser.add_option("-o", "--obsid", dest="obsid", default=None, type=int, help="Observation's ID")
parser.add_option("-d", "--datadir", dest="datadir", default=None, type=str, help="Directory where data will be stored")

opts, args = parser.parse_args()

# At least the observation that is to be updated needs to be known
if opts.obsid is None:
    parser.error("Obsid must be set")

con = lite.connect(DB_FILE)
with con:
    cur = con.cursor()
    cur.execute("INSERT INTO Log (Obsid, Datadir, Status) VALUES(?, ?, ?)", (opts.obsid, opts.datadir, "Initialised"))
