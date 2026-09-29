# Simple function to check if SQL queries that populate source data were run today
# if not, run and log today's date in tracking file, otherwise skip

from datetime import date
import hadoop
import os

# simple text file for store date of latest data refresh
# (which is now limited to May 4, 2026 since I left the company)
TRACK_FILE = 'SelectionEvaluator/last_run.txt'

def check():

    # short circuit function since no access to database
    #today = str(date.today())
    today = "2026-05-04"

    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, 'r') as f:
            last_run = f.read().strip()
            if last_run != today:
                print("Last run stored date did not match today's date of ", today)
                print("Pulling fresh data...")
                hadoop.refreshData()
    else:
        print("last_run.txt file missing! Unable to refresh data.")