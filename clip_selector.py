#!/usr/bin/python3
# Select clips from creators
# Keep in mind view count, duration to till 10mins and avoid duplicates
from pathlib import Path
import random
import argparse
import datetime
from dateutil.relativedelta import relativedelta

import pandas as pd
from InquirerPy import prompt

from db.mydb import Mydb
from model.cluster import CLUSTERS

URLS = Path('./urls')

def get_past_date(days='7'):
    days = int(days)
    TODAY = datetime.date.today()
    date = TODAY - relativedelta(days=days)
    return str(date.isoformat())

def read_clips_df_from_db(creators):
    MYDB = Mydb()
    # Read sqlite query results into a pandas DataFrame
    creators_str = '('+','.join([f"'{c}'" for c in creators])+')'
    df = pd.read_sql_query(f"SELECT * FROM clips WHERE creator IN {creators_str}", MYDB.con)
    # Verify that result of SQL query is stored in the dataframe
    print(df.head())
    # Close connection
    MYDB.con.close()
    return df

def discard_invalid_clips(df, args):
    df = df[df['published']==0]
    df = df[df['time'] >= get_past_date(days=int(args.days))]
    return df

def select_clips(df, args):
    df_select = pd.DataFrame()
    # Select best clips
    max_duration = int(args.max_duration)
    duration = 0

    # Select 2 highest views clips
    df.sort_values(by=['views','duration'])
    count = 0
    n_first = int(args.n_first)
    top_clips = []
    for _, row in df.iterrows():
        duration += row.duration
        top_clips.append(row)
        count += 1
        if count >= n_first:
            break


    # Pick from creators
    clips = []
    creators = list(df['creator'].unique())
    for creator in creators*10:
        for _, row in df.iterrows():
            if row.creator != creator:
                continue
            if row.url in [x['url'] for x in top_clips]:
                continue
            if row.url in [x['url'] for x in clips]:
                continue
            if row.duration + duration > max_duration:
                continue
            # Add
            clips.append(row)
            duration += row.duration
            break

    random.shuffle(clips)
    clips = top_clips + clips
    df_select = pd.concat(clips, axis=1).T
    # Shuffle 
    return df_select

def select_clips_prompt(df, args):
    #creators = CLUSTERS.by_name(args.cluster).names # Can give errors, no clips 
    creators = list(df['creator'].unique())
    clips = []
    duration = 0
    df.sort_values(by=['views','duration'])
    while duration <= int(args.max_duration):
        # Setup prompt
        status_str = [f'duration: {duration}']
        nclips = {}
        viewtime = {}
        for c in creators:
            nclips[c] = sum([x['creator'] == c for x in clips])
            viewtime[c] = sum(int(x['duration']) if x['creator'] == c else 0 for x in clips)
            status_str.append(f"{c}:{nclips[c]} {viewtime[c]}s")
        status_str = ';'.join(status_str)

        choices = ['pick_max_view', 'pick_low_n', 'pick_low_duration']

        count = {}
        for x in creators:
            count[x] = 0
        max = 1
        for _, row in df.iterrows():
            if count[row.creator] >= max:
                continue
            url = row['url']
            if url in [x['url'] for x in clips]:
                continue
            str = f'{row.creator} {row.views} {row.duration} {row.time}'
            choices.append(str)
            count[row.creator] += 1
        questions = [
            {
                'type': 'list',
                'name': 'clips',
                'message': 'Select {}'.format(status_str),
                'choices': choices,
            },
        ]
        answers = prompt(questions)
        answer = answers['clips']

        # Custom commands to select answer for us
        if answer == 'pick_low_n':
            creator = min(nclips, key=nclips.get)
            for x in choices[2:]:
                if creator in x:
                    answer = x
                    break

        if answer == 'pick_low_duration':
            creator = min(viewtime, key=viewtime.get)
            for x in choices[2:]:
                if creator in x:
                    answer = x
                    break

        if answer == 'pick_max_view':
            row = df.loc[df['views'].idxmax()].T
            answer = str = f'{row.creator} {row.views} {row.duration} {row.time}'

        creator, views, dur, time = answer.split(' ')
        for _, row in df.iterrows():
            if row.creator != creator:
                continue
            if row.views != int(views):
                continue
            if row.duration != int(dur):
                continue
            if row.time != time:
                continue
            # Add
            clips.append(row)
            duration += int(row.duration)
            break
    df_select = pd.concat(clips, axis=1).T
    return df_select


def main(args):
    creators = CLUSTERS.by_name(args.cluster).names
    df = read_clips_df_from_db(creators)
    df = discard_invalid_clips(df, args)
    #df_clips = select_clips(df, args)
    df_clips = select_clips_prompt(df, args)
    Path('urls.txt').write_text('\n'.join(df_clips['url']))

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("cluster", default="cluster1", help="clustername ex. cluster1")
    parser.add_argument("days", default='7', help="7 or 30")
    parser.add_argument("n_first", default='2', help="2 highest view clips first")
    parser.add_argument("max_duration", default='610', help="duration in seconds")
    return parser.parse_args()

if __name__ == "__main__":
    args = argparser()
    main(args)
