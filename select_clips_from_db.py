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

from model.mydb import Mydb
from model.cluster import CLUSTERS
from model.clips import Clip, Compilation
from model.cluster import Creator


class ClipsSelector:
    def __init__(self, args):
        self.creators = get_list_creators(args)
        self.clips = []
        self.nclips = {}
        self.viewtime = {}
        self.duration = 0
        self.df = self._read_clips_from_db(args)
        self.commands = ['pick_max_view', 'pick_low_n', 'pick_low_duration']

    def _read_clips_from_db(self, args):
        def read_clips_from_db(args):
            db = Mydb()
            if args.category:
                df = db.read_clips_categories_df_from_db(args.cluster)
            else:
                df = db.read_clips_creators_df_from_db(self.creators)
            db.close()
            return df
        def discard_invalid_clips(df, args):
            def _date_n_days_ago(days: str ='7') -> str:
                days = int(days)
                today = datetime.date.today()
                date = today - relativedelta(days=days)
                return str(date.isoformat())
            if not args.published_ok:
                # Only keep clips that have not been published
                df = df[df['published']==0]
            # Ignore broken clips
            df = df[df['broken']==0]
            # Filter lang
            df = df[df['language']==args.lang]
            # Only keep clips between args.days and now
            df = df[df['created_at']>=_date_n_days_ago(days=args.days)]
            return df
        df = read_clips_from_db(args)
        df = discard_invalid_clips(df, args)
        return df.sort_values(by=['view_count','duration']) 

    def load_compilation(self, compilation_with_errors: Compilation):
        # Setup where we left off
        # Update DB with existing compilation
        errors = [e for e in compilation_with_errors if e.error]
        db = Mydb()
        for u in [e.clip.url for e in errors]:
            db.set_broken(u)
            print(f'Set broken url:\n\t{u}')
        db.commit()
        db.close()
        # Sort compilation_with_errors
        compilation_without_errors = [e for e in compilation_with_errors if not e.error]
        sorted_compilation_without_errors = sorted(compilation_without_errors, key=lambda e: e.order)
        self.clips = [e.clip for e in sorted_compilation_without_errors]
        self.duration = sum([c.duration for c in self.clips])
        # Read clips from db
        self.df = self._read_clips_from_db(args)
        # Update nview, viewcount dicts
        self.update()

    def update(self):
        for c in self.creators:
            self.nclips[c] = sum([x.creator == c for x in self.clips])
            self.viewtime[c] = sum(int(x.duration) if x.creator == c else 0 for x in self.clips)


    def add_selected_clip(self, choice: Clip, position: int = -1):
        if position == -1:
            self.clips.append(choice)
        else:
            self.clips.insert(position, choice)
        self.duration += int(choice.duration)

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

    def prompt_choices(self):
        def _status_text(self) -> str:
            status_str = [f'duration: {self.duration}']
            for c in self.creators:
                status_str.append(f"{c}:{self.nclips[c]} {self.viewtime[c]}s")
            return ';'.join(status_str)
        def _gen_choices(self) -> list:
            choices = []
            count = {}
            for x in self.creators:
                count[x] = 0
            max = 2
            for _, row in self.df.iterrows():
                if count[row.creator] >= max:
                    continue
                url = row['url']
                if url in [x.url for x in self.clips]:
                    continue
                choices.append(Clip(from_row=True,row=row))
                count[row.creator] += 1
            self.choices = choices
            self.choices_str = [c.to_string() for c in choices]
            return self.commands + self.choices_str
        choices = _gen_choices(self)
        questions = [
            {
                'type': 'list',
                'name': 'clips',
                'message': 'Select {}'.format(_status_text(self)),
                'choices': choices,
            },
        ]
        answers = prompt(questions)
        return answers['clips']

    def parse_answer_from_command(self, cmd):
        # Custom commands to select answer for us
        if cmd == 'pick_low_n':
            answer = self.pick_low_n(self.choices)
        elif cmd == 'pick_low_duration':
            answer = self.pick_low_duration(self.choices)
        elif cmd == 'pick_max_view':
            # Pick max views from answer
            max = 0
            maxc = None
            for c in self.choices:
                views = int(c.view_count) 
                if views > max:
                    maxc = c
                    max = views
            answer = maxc.to_string()
        return answer

    def prompt_and_select_add_clip(self, answer):
        answer = self.parse_answer_from_command(answer) if answer in self.commands else answer
        idx = self.choices_str.index(answer)
        clip = self.choices[idx]
        self.add_selected_clip(clip)
        self.update()

class SelectionPrompt:
    def __init__(self):



def get_list_creators(args) -> list:
    # returns list of Creator
    if args.creators:
        creators = list(map(Creator, args.cluster))
    else:
        creators = []
        for c in args.cluster:
            creators += CLUSTERS.by_name(c).creators
    return creators

def select_clips_from_db(args):
    sh = ClipsSelector(args)
    if args.cont:
        compilation_with_errors = Compilation.load(args.wd / 'compilation.pkl')
        sh.load_compilation(compilation_with_errors)
    while sh.duration <= int(args.duration):
        answer = sh.prompt_choices()
        sh.prompt_and_select_add_clip(answer)
    df_clips = sh.clipshhhhhhhhhhh
    # Write to url.txt
    comp = Compilation()
    for clip in df_clips:
        comp.add(clip)
    comp.dump(args.wd / Path('compilation.pkl'))
    (args.wd / Path('./urls.txt')).write_text('\n'.join([x.url for x in df_clips]))

def create_compilation_from_db(args):
    # Create compilation
    # Clips ordered
    # Choices prompts
    # Edit compilation with prompts
    # new file edit_compilation?
    # prolly same file since selecting new happens here
    comp = Compilation()
    df_clips = select_clips(args)
    # Write to url.txt
    comp = Compilation()
    for clip in df_clips:
        comp.add(clip)
    comp.dump(args.wd / Path('compilation.pkl'))
    (args.wd / Path('./urls.txt')).write_text('\n'.join([x.url for x in df_clips]))


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('cluster', nargs='+', default='cluster1', help='clustername ex. cluster1')
    parser.add_argument('--project', default="default", help='name of project dir')
    parser.add_argument('--days', default='7', help='ex. 7 or 30')
    parser.add_argument('--duration', default='610', help='duration in seconds')
    parser.add_argument('--published_ok', action='store_true', help='set to include clips that have already been published')
    parser.add_argument("--creators", action="store_true", help="set if list of creators")
    parser.add_argument("--cont", action="store_true", help="continue selection from urls.txt and error.txt after errors")
    parser.add_argument('--lang', default='en', help='set language ex. en, fr, es, ko, en-gb')
    parser.add_argument("--category", action="store_true", help="set if input is category ex 'Just Chatting'")
    return parser.parse_args()

if __name__ == '__main__':
    args = argparser()
    args.wd = Path(args.project)
    select_clips_from_db(args)
