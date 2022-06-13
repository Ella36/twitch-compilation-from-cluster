#!/usr/bin/python3
# Select clips from creators
# Keep in mind view count, duration to till 10mins and avoid duplicates
from pathlib import Path
import argparse
import datetime
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass

import pandas as pd
from InquirerPy import prompt

from db.mydb import Mydb
from model.cluster import CLUSTERS
from model.clip import Clip

URLS = Path('./urls')

def date_n_days_ago(days: str ='7') -> str:
    days = int(days)
    today = datetime.date.today()
    date = today - relativedelta(days=days)
    return str(date.isoformat())

def read_clips_df_from_db(creators: list):
    db = Mydb()
    # Read sqlite query results into a pandas DataFrame
    creators_str = '('+','.join([f"'{c.name}'" for c in creators])+')'
    df = pd.read_sql_query(
        f"SELECT * FROM clips WHERE creator IN {creators_str}",
        db.con
    )
    # Verify that result of SQL query is stored in the dataframe
    print(df.head())
    # Close connection
    db.con.close()
    return df

def discard_invalid_clips(df, args):
    if not args.published_ok:
        # Only keep clips that have not been published
        df = df[df['published']==0]
    # Only keep clips between args.days and now
    df = df[df['time']>=date_n_days_ago(days=args.days)]
    return df

class SelectionHelper:
    def __init__(self, creators, df):
        self.creators = creators
        self.clips = []
        self.nclips = {}
        self.viewtime = {}
        self.duration = 0
        self.df = df
        self.df.sort_values(by=['views','duration']) 
        self.commands = ['pick_max_view', 'pick_low_n', 'pick_low_duration']

    def update(self):
        for c in self.creators:
            self.nclips[c] = sum([x.row.creator == c for x in self.clips])
            self.viewtime[c] = sum(int(x.row.duration) if x.row.creator == c else 0 for x in self.clips)

    @property
    def status_text(self) -> str:
        status_str = [f'duration: {self.duration}']
        for c in self.creators:
            status_str.append(f"{c}:{self.nclips[c]} {self.viewtime[c]}s")
        return ';'.join(status_str)

    def add_selected_clip(self, choice: Clip):
        self.clips.append(choice)
        self.duration += int(choice.row.duration)

    def pick_low_n(self, choices):
        creator = min(self.nclips, key=self.nclips.get)
        for x in choices[2:]:
            if creator in x:
                return x

    def pick_low_duration(self, choices):
        creator = min(self.viewtime, key=self.viewtime.get)
        for x in choices[2:]:
            if creator in x:
                return x

    def gen_choices(self):
        choices = []
        count = {}
        for x in self.creators:
            count[x] = 0
        max = 1
        for _, row in self.df.iterrows():
            if count[row.creator] >= max:
                continue
            url = row['url']
            if url in [x.row.url for x in self.clips]:
                continue
            choices.append(Clip(row))
            count[row.creator] += 1
        self.choices = choices
        self.choices_str = [str(c) for c in choices]
        return self.commands + self.choices_str

@dataclass
class Clip:
    row: pd.Series
    def __str__(self):
        return f'{self.row.creator} {self.row.views} {self.row.duration} {self.row.time}'

def select_clips_prompt(df, args):
    creators = list(df['creator'].unique())
    sh = SelectionHelper(creators, df)
    while sh.duration <= int(args.max_duration):
        # Setup prompt
        sh.update()
        choices = sh.gen_choices()
        questions = [
            {
                'type': 'list',
                'name': 'clips',
                'message': 'Select {}'.format(sh.status_text),
                'choices': choices,
            },
        ]
        answers = prompt(questions)

        answer = answers['clips']

        # answer is str version of Clip.row
        # Check if answer in commands
        if answer in sh.commands:
            # Custom commands to select answer for us
            if answer == 'pick_low_n':
                answer = sh.pick_low_n(choices)
            elif answer == 'pick_low_duration':
                answer = sh.pick_low_duration(choices)
            elif answer == 'pick_max_view':
                # Pick max views from answer
                max = 0
                maxc = None
                for c in sh.choices:
                    views = int(c.row.views) 
                    if views > max:
                        maxc = c
                        max = views
                answer = str(maxc)
        # Find index of then that index is choices[i] -> row
        idx = sh.choices_str.index(answer)
        clip = sh.choices[idx]
        sh.add_selected_clip(clip)
    return pd.concat([x.row for x in sh.clips], axis=1).T

def get_list_creators(args) -> list:
    # returns list of Creator
    creators = CLUSTERS.by_name(args.cluster).creators
    return creators

def main(args):
    creators = get_list_creators(args)
    df = read_clips_df_from_db(creators)
    df = discard_invalid_clips(df, args)
    df_clips = select_clips_prompt(df, args)
    Path('urls.txt').write_text('\n'.join(df_clips['url']))

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('cluster', default='cluster1', help='clustername ex. cluster1')
    parser.add_argument('days', default='7', help='ex. 7 or 30')
    parser.add_argument('n_first', default='2', help='2 highest view clips first')
    parser.add_argument('max_duration', default='610', help='duration in seconds')
    parser.add_argument('published_ok', action='store_true', help='set to include clips that have already been published')
    return parser.parse_args()

if __name__ == '__main__':
    args = argparser()
    main(args)
