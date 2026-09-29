# This should no longer run since 'today' is hard-coded to be date of last run (5/4/26)
import pandas as pd
import pyodbc
import os
from datetime import date

TRACK_FILE = "last_run.txt"

def refreshData():

    today = str(date.today())

    filesToRefresh = [('SQL/active_mmac.sql', 'Data/active_mmac.csv'), 
                    ('SQL/feature_synonyms.sql', 'Data/ftr_syn_table.csv'),
                    ('SQL/model_synonyms.sql', 'Data/mdl_syn_table.csv')]

    conn = pyodbc.connect("DSN=PPS IMPALA", autocommit=True)

    for filepath, filename in filesToRefresh:

        with open(filepath, 'r') as file:
            sql_query = file.read()

        df = pd.read_sql(sql_query, conn)
        df.to_csv(filename, index=False)

    # log date of last run
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, 'w') as f:
            f.write(today)
    else:
        print('last_run.txt not found!')