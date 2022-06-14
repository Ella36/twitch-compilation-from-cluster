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
from model.cluster import Creator


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
    def __init__(self, creators, df, fix_errors=False):
        self.creators = creators
        self.clips = []
        self.nclips = {}
        self.viewtime = {}
        self.duration = 0
        self.df = df
        self.df.sort_values(by=['views','duration']) 
        self.commands = ['pick_max_view', 'pick_low_n', 'pick_low_duration']
        if fix_errors:
            self.fix_error()

    def fix_error(self):
        urls = read_urls()
        errors = read_errors()
        db = Mydb()
        broken_idx = []
        i = 0
        for u in urls:
            if u in errors:
                broken_idx.append(i)
                #db.set_broken(u)
                continue
            for _, row in self.df.iterrows():
                if row.url == u:
                    self.clips.append(Clip(row))
                    self.duration += int(row.duration)
            i += 1
        self.update()
        db.commit()
        # Select and fill
        broken_idx.reverse()
        for i in broken_idx:
            # Prompt for fixes
            choices = self.gen_choices()
            questions = [
                {
                    'type': 'list',
                    'name': 'clips',
                    'message': 'Select {}'.format(self.status_text),
                    'choices': choices,
                },
            ]
            answers = prompt(questions)

            answer = answers['clips']

            # answer is str version of Clip.row
            # Check if answer in commands
            if answer in self.commands:
                # Custom commands to select answer for us
                if answer == 'pick_low_n':
                    answer = self.pick_low_n(choices)
                elif answer == 'pick_low_duration':
                    answer = self.pick_low_duration(choices)
                elif answer == 'pick_max_view':
                    # Pick max views from answer
                    max = 0
                    maxc = None
                    for c in self.choices:
                        views = int(c.row.views) 
                        if views > max:
                            maxc = c
                            max = views
                    answer = str(maxc)
            # Find index of then that index is choices[i] -> row
            idx = self.choices_str.index(answer)
            clip = self.choices[idx]
            self.add_selected_clip(clip, position=i)
        df_clips = pd.concat([x.row for x in self.clips], axis=1).T
        Path('urls.txt').write_text('\n'.join(df_clips['url']))


    def fill_in_clips(self, urls):
        for _, row in self.df.iterrows():
            if row.url in urls:
                self.clips.append(Clip(row))
                self.duration += int(row.duration)
        self.update()

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

    def add_selected_clip(self, choice: Clip, position: int = -1):
        if position == -1:
            self.clips.append(choice)
        else:
            self.clips.insert(position, choice)
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
        print(self.row.time)
        return f'{self.row.creator} {self.row.views} {self.row.duration} {self.row.time}'

def read_urls():
    return Path('./urls.txt').read_text().strip().split('\n')

def read_errors():
    return Path('./errors.txt').read_text().strip().split('\n')

def select_clips_prompt(df, args):
    creators = list(df['creator'].unique())
    if args.cont:
        sh = SelectionHelper(creators, df, fix_errors=True)
    else: 
        sh = SelectionHelper(creators, df)
    while sh.duration <= int(args.duration):
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


def get_list_creators(args) -> list:
    # returns list of Creator
    if args.creators:
        creators = list(map(Creator, args.cluster))
    else:
        creators = []
        for c in args.cluster:
            creators += CLUSTERS.by_name(c).creators
    return creators

def select_clips(args):
    creators = get_list_creators(args)
    df = read_clips_df_from_db(creators)
    df = discard_invalid_clips(df, args)
    df_clips = select_clips_prompt(df, args)
    # Write to url.txt
    Path('urls.txt').write_text('\n'.join(df_clips['url']))
    # Write to table in database
    # So we can change flags publish later

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('cluster', nargs='+', default='cluster1', help='clustername ex. cluster1')
    parser.add_argument('--days', default='7', help='ex. 7 or 30')
    parser.add_argument('--duration', default='610', help='duration in seconds')
    parser.add_argument('--published_ok', action='store_true', help='set to include clips that have already been published')
    parser.add_argument("--creators", action="store_true", help="set if list of creators")
    parser.add_argument("--cont", action="store_true", help="continue selection from urls.txt and error.txt after errors")
    return parser.parse_args()

if __name__ == '__main__':
    args = argparser()
    select_clips(args)
