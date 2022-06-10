#!/usr/bin/python3
# Select clips from creators
# Keep in mind view count, duration to till 10mins and avoid duplicates
import pandas as pd
from pathlib import Path
import random
from datetime import datetime

URLS = Path('./urls')

# Select cluster
from cluster.cluster import CLUSTERS
cluster = 'cluster1'
creators = CLUSTERS.by_name(cluster).names

import pandas as pd
from db.mydb import Mydb
MYDB = Mydb()

# Read sqlite query results into a pandas DataFrame
creators_str = '('+','.join([f"'{c}'" for c in creators])+')'
df = pd.read_sql_query(f"SELECT * FROM clips WHERE creator IN {creators_str}", MYDB.con)

# Verify that result of SQL query is stored in the dataframe
print(df.head())

# Close connection
MYDB.con.close()

# Discard invalid clips
df = df[df['published']==0]

import datetime
from dateutil.relativedelta import relativedelta
def get_past_date(days=7):
    TODAY = datetime.date.today()
    date = TODAY - relativedelta(days=days)
    return str(date.isoformat())

days = 7
df = df[df['time'] >= get_past_date(days=days)]

# Select best clips
max_duration = 610
duration = 0
top_urls = []

# Select 2 highest views clips
count = 0
n_high_view_first = 2
df.sort_values(by=['views','duration'])
for idx, row in df.iterrows():
    top_urls.append(row.url)
    duration += row.duration
    if len(top_urls) >= n_high_view_first:
        break

# Pick from creators
urls = []
for creator in creators*10:
    for idx, row in df.iterrows():
        if row.creator != creator:
            continue
        if row.url in urls:
            continue
        if row.duration + duration > max_duration:
            continue
        # Add
        urls.append(row.url)
        duration += row.duration
        break

random.shuffle(urls)

Path('urls.txt').write_text('\n'.join(top_urls+urls))
