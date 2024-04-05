#!/usr/bin/env python
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
import argparse
import datetime
import math
import random

from InquirerPy import prompt

from cfg.data import PROJECTS
from model.mydb import Mydb


@dataclass
class Release:
    name: str
    interval: int


class Day:
    def __init__(self, releases):
        self.releases = releases

    def add(self, release):
        self.releases.append(release)

    @property
    def cost(self):
        return sum([r.interval for r in self.releases])

    def __str__(self):
        return f'{self.cost}-' + ', '.join([str(r) for r in self.releases])


class ReleaseSolver:
    def __init__(self, initial, target_interval_per_day):
        self.initial = initial  # Array to manipulate
        self.n_iterations = 1000
        self.target_interval_per_day = target_interval_per_day

    def cost(self, candidate):
        avg_interval_day_cost = sum(
            [abs(self.target_interval_per_day-d.cost) for d in candidate])
        spread_cost = 0
        for day_idx, d in enumerate(candidate):
            for r in d.releases:
                release_name = r.name
                # Search for closest release_name
                for day2_idx, d2 in enumerate(candidate):
                    n = [r2.name.split('_')[0] for r2 in d2.releases].count(
                        release_name.split('_')[0])
                    if day2_idx == day_idx:
                        n -= 1
                    spread_cost += abs(n*(r.interval - abs(day2_idx-day_idx)))
        return avg_interval_day_cost * 2 + spread_cost / 10  # Guessing with /3

    def manipulate(self, current, step_size):
        return current

    def shuffle(self, current):
        releases = []
        for d in current:
            releases += d.releases
        releases_copy = releases[:]
        random.shuffle(releases_copy)
        output = [Day([]) for _ in range(30)]
        i = 0
        while len(releases_copy) > 0:
            i += 1
            i = i % 30
            r = releases_copy.pop()
            output[i].add(r)
        random.shuffle(output)
        return output

    def simulated_annealing(self, temp=1000):
        # Setup best
        best = self.initial[:]
        best_eval = self.cost(self.initial[:])
        print(f"Initial cost: {best_eval:.2f}")
        # current working solution
        curr, curr_eval = best, best_eval
        for i in range(self.n_iterations):
            # take a step
            candidate = self.shuffle(curr)
            candidate_eval = self.cost(candidate)
            if candidate_eval < best_eval:
                # Store new best
                best, best_eval = candidate, candidate_eval
            # difference between candidate and current point
            diff = candidate_eval - curr_eval
            # calculate temperature for current epoch
            t = temp / float(i+1)
            # calculate metropolis acceptance cirterion
            metropolis = math.exp(-diff / t)
            # check if keep new point
            if diff < 0 or random.random() < metropolis:
                # store new current point
                curr, curr_eval = candidate, candidate_eval
        return [best, best_eval]


def is_prompt_confirm(step: str):
    questions = [
        {
            'type': 'confirm',
            'message': f'Do you want to {step}?',
            'name': 'confirm',
            'default': True,
        },
    ]
    answers = prompt(questions)
    return answers['confirm']


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--today", action="store_true",
                        help="ignores date and starts from today")
    parser.add_argument('-d', '--date', default='2022-07-21',
                        help='start date in format: YYYY-MM-DD')
    return parser.parse_args()


def print_days_since_release():
    db = Mydb()
    df = db.read_compilations_df_from_db()
    latest_release_by_category = {}
    for _, row in df.iterrows():
        # print(row.id, row.time, row.project)
        published_at = datetime.datetime.strptime(row.time, "%Y-%m-%d")
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


if __name__ == '__main__':
    args = argparser()
    # List days since last release
    print_days_since_release()
    print(f"\n{'-'*40}\n")
    # Create release schedule

    # Videos to release
    releases = []
    for p in PROJECTS.projects:
        if not p.is_active:
            continue
        releases += [Release(p.name, p.interval)] * p.n_per_month
    n = len(releases)
    print(f'Videos to release:\n\tn {n}')

    # Create schedule
    if args.today:
        start_time = datetime.datetime.utcnow()
    else:
        start_time = datetime.datetime.fromisoformat(args.date)
    print(f"\n{'-'*40}\n")

    # calculate avg interval
    target_interval_per_day = sum(
        [r.interval for r in releases]
    ) / 30
    print(f'Target interval goal: {target_interval_per_day:.2f}')

    is_generated_schedule = False
    while is_prompt_confirm('Generate a new schedule'):

        releases_copy = releases[:]
        initial_release_by_day = [Day([]) for _ in range(30)]
        i = 0
        while len(releases_copy) > 0:
            i += 1
            i = i % 30
            r = releases_copy.pop()
            initial_release_by_day[i].add(r)
        release_solver = ReleaseSolver(
            initial_release_by_day, target_interval_per_day)
        releases_by_day, cost = release_solver.simulated_annealing()

        n = sum([len(d.releases) for d in releases_by_day])
        print(f'Videos released:\n\tn {n}')

        for i, day in enumerate(releases_by_day):
            time = start_time + timedelta(days=i)
            day_format = ', '.join([r.name for r in day.releases])
            print(f'{i:02d} {time.date()} {day.cost} {day_format}')
        is_generated_schedule = True

    if is_generated_schedule:
        # Write solution somewhere
        schedule = {}  # 'date': isoformat, 'projects': list str
        for i, day in enumerate(releases_by_day):
            time = start_time + timedelta(days=i)
            project_names = [r.name for r in day.releases]
            date = str(time.date())
            schedule[date] = project_names

    file = Path('./schedule.text')
    if is_generated_schedule:
        text = ''
        for date, project_names in schedule.items():
            text += '-\n'
            text += f'{date}\n'
            if len(project_names) != 0:
                text += '\n'.join(project_names) + '\n'
        file.write_text(text)

    if not is_generated_schedule or is_prompt_confirm('Read schedule from schedule.txt'):
        schedule = {}
        text = file.read_text().strip().split('\n')
        for i, line in enumerate(text):
            if line == '-':
                # Begin new dateproj
                if text[i+1] == '-':
                    # No release this day
                    continue
                date = text[i+1]
                project_names = []
                for e in text[i+2:]:
                    if e == '-':
                        break
                    project_names.append(e)
                schedule[date] = project_names

    # Generate commands
    if is_prompt_confirm('Generate commands from schedule.txt'):
        out = 'Date, project name, commands'
        group_by_count = 0
        for date, project_names in schedule.items():
            group_by_count += 1
            if group_by_count % 5 == 0:
                out += f'{"-"*40}\n'
                group_by_count = 0
            out += f'{date} {", ".join(project_names)}\n'
            for p in project_names:
                out += f'./create_compilation_from_project.py --project {p} --dir 1\n'
                pf = f'./proj-{p}-1'
        print(out)
        # Write to file
        if is_prompt_confirm('Write commands to cmds.txt'):
            file = Path('./cmds.txt')
            with file.open('w') as f:
                f.write(out)
