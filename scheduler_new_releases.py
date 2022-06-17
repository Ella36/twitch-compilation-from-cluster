#!/usr/bin/python3
# List dates when new releases should be made
import argparse
from pathlib import Path
import uuid

from InquirerPy import prompt

from model.clips import Compilation
from model.mydb import Mydb
from publish import publish

from cfg.data import PROJECTS

def argparser():
    parser = argparse.ArgumentParser()
    #parser.add_argument('cluster', nargs='+', default='cluster1', help='clustername ex. cluster1')
    ## Database
    #parser.add_argument('-co', '--compilations', action='store_true', help='create table compilations')
    #parser.add_argument('-c', '--clips', action='store_true', help='create table clips')
    #parser.add_argument('--sync', action='store_true', help='update published flag from compilations')
    ## Confirm
    #parser.add_argument("--confirm", action="store_true", help="autoconfirms")
    ## Search for clips
    #parser.add_argument("--creators", action="store_true", help="set if list of creators")
    #parser.add_argument("--category", action="store_true", help="set if input is category ex 'Just Chatting'")
    #parser.add_argument("--days", default="30", help="pick n days")
    #parser.add_argument("--project", default="default", help="name of project, creates working directory")
    ## Select clips
    #parser.add_argument("--cont", action="store_true", help="continue selection from urls.txt")
    #parser.add_argument('--duration', default='610', help='duration in seconds')
    #parser.add_argument('--published_ok', action='store_true', help='set to include clips that have already been published')
    #parser.add_argument('--lang', default='en', help='set language ex. en, fr, es, ko')
    ## Downloader
    #parser.add_argument("--resolution", default='720')
    ## Input formatter
    #parser.add_argument("--skip_draw", action="store_true")
    ## Merger
    return parser.parse_args()

import datetime
if __name__ == '__main__':
    args = argparser()
    db = Mydb()
    # Check each project.
    #   List days since last release
    df = db.read_compilations_df_from_db()
    latest_release_by_category = {}
    for _, row in df.iterrows():
        #print(row.id, row.time, row.project)
        published_at = datetime.datetime.strptime("2022-06-14", "%Y-%m-%d")
        now = datetime.datetime.utcnow()
        days_since = (now - published_at).days
        latest_release = latest_release_by_category.get(row.project)
        if latest_release is None or days_since < latest_release:
            latest_release_by_category[row.project] = days_since

    print(f"{'category':20} {'days_since_release':3}")
    print(f"{'-'*20}-{'-'*20}")
    for category, days_since_release in latest_release_by_category.items():
        print(f"{category:20} {days_since_release:3}")
    db.close()

    vids_per_month = sum(i.n_per_month for i in PROJECTS.projects)
    print(vids_per_month)
