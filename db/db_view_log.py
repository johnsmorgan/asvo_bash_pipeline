import os, datetime
import sqlite3 as lite
from optparse import OptionParser
from dateutil.relativedelta import relativedelta

# Initialise where database file is stored (in .bashrc)
DB_FILE = os.environ['DB_FILE']

# Options that may be selected as to view database log
parser = OptionParser()
parser.add_option("-o", "--obsid", dest="obsid", default=None, type=int, help="Observation's ID")
parser.add_option("-u", "--unfinished", dest="unfinished", action="store_true", help="Print only the jobs that have not been completed")
parser.add_option("-c", "--completed", dest="completed", action="store_true", help="Print only completed jobs")
parser.add_option("-p", "--processing", dest="processing", action="store_true", help="Print only the jobs that are currently processing on Garrawarla")
parser.add_option("-a", "--asvo", dest="asvo", action="store_true", help="Print only jobs that are currently processing on ASVO")
parser.add_option("-f", "--failed", dest="failed", action="store_true", help="Print only the jobs that have failed")
parser.add_option("-r", "--recent", dest="recent", metavar="HOURS", default=None, type=float, help="Print only jobs that have started in the last N hours")
parser.add_option("-n", "--number", dest="number", metavar="N", default=10, type=int, help="Number of jobs to print out")
parser.add_option("--all", dest="all", action="store_true", help="Print all jobs")
parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="Print out the query that is accessing the database")

opts, args = parser.parse_args()

# Creation of query that will be used to access the database based on user options
query = "SELECT * FROM Log"

if opts.obsid is not None:
    query += ''' WHERE Obsid=%d''' % (opts.obsid)
elif opts.unfinished:
    query += " WHERE Ended IS NULL"
elif opts.completed:
    query += ''' WHERE Status="Completed"'''
elif opts.processing:
    query += ''' WHERE Status="Processing"'''
elif opts.asvo:
    query += ''' WHERE Status="Processing on ASVO"'''
elif opts.failed:
    query += ''' WHERE Status="Failed"'''
elif opts.recent is not None:
    query += ''' WHERE Started > "%s"''' % str(datetime.datetime.now() - relativedelta(hours=opts.recent))

if opts.number != 10:
    query += ''' LIMIT %d''' % (opts.number)

if opts.verbose:
    print(query)

# Access all relevant rows of database based on user options
con = lite.connect(DB_FILE)
with con:
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchall()

# Used to calculate the current run time of a processing observation
current_time = datetime.datetime.now()

# Depending on the status of the observation and the user options, different messages will be printed to the terminal
for row in rows:
    print(f"Obsid: %d" % row[1])
    print(f"Current Status: %s" % row[9])
    if row[9] == "Processing on ASVO":
        print(f"ASVO Job ID: %d" % row[2])
        print(f"Time Job Submitted: %s UTC" % row[3][:19])
    elif row[9] == "Processing":
        print(f"ASVO Job ID: %d" % row[2])
        print(f"Time Job Submitted: %s UTC" % row[3][:19])
        print(f"Data Directory: %s" % row[4])
        print(f"Slurm JobID: %d" % row[5])
        print(f"Time Job Started: %s UTC" % row[6][11:19])

        start_time = datetime.datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S.%f')
        diff = current_time - start_time
        diff_m = (diff.total_seconds())/60
        diff_s = (diff_m - (diff.total_seconds()//60))*60
    
        if diff_m > 60:
            diff_h = diff_m / 60
            diff_m = (diff_h - diff_m//60)*60
            print(f"Current Run Time: %dh%dm%ds" % (diff_h, diff_m, diff_s))    
        else:
            print(f"Current Run Time: %dm%ds" % (diff_m, diff_s))
    elif row[9] == "Completed":
        print(f"ASVO Job ID: %d" % row[2])
        print(f"Time Job Submitted: %s UTC" % row[3][:19])
        print(f"Data Directory: %s" % row[4])
        print(f"Slurm JobID: %d" % row[5])
        print(f"Time Job Started: %s UTC" % row[6][11:19])
        print(f"Time Job Completed: %s UTC" % row[7][11:19])
        
        duration_s = row[8]
        duration_m = duration_s / 60
        leftover_s = (duration_m - (duration_s//60))*60

        if duration_m > 60:
            duration_h = duration_m / 60
            leftover_m = (duration_h - (duration_m//60))*60
            print(f"Total Run Time: %dh%dm%ds" % (duration_h, leftover_m, leftover_s))
        else:
            print(f"Total Run Time: %dm%ds" % (duration_m, leftover_s))
    elif row[9] == "Failed":
        print(f"Error Occurred")
        if row[2] == None:
            print(f"Failed to Submit on ASVO")
        elif (row[2] != None) and (row[5] == None):
            print(f"Failed to Queue job on Garrawarla")
            print(f"Time Job Submitted: %s UTC" % row[3][:19])
            print(f"Time Failed: %s UTC" % row[7][11:19])
        elif (row[2] != None) and (row[5] != None):
            print(f"Failed process on Garrawarla, check log file")
            print(f"Time Job Submitted: %s UTC" % row[3][:19])
            print(f"Time Job Started: %s UTC" % row[6][11:19])
            print(f"Time Job Failed: %s UTC" % row[7][11:19])
    print(f" ")
