#!/usr/bin/python3
from pathlib import Path
import datetime

from InquirerPy import prompt

from model.mydb import Mydb


def update_publish_flags_db(urls):
        db = Mydb()
        for u in urls:
            db.set_publish(u)
        db.commit()
        db.con.close()

def write_script_to_db(urls):
    db = Mydb()
    def _extract_data(u):
        values = db.lookup_url(u)
        return {
            'creator': values[0],
            'duration': int(values[2]),
            }
    data = list(map(_extract_data, urls))
    creators = ','.join([x['creator'] for x in data])
    urls_joined = ','.join(urls)
    duration = sum([x['duration'] for x in data])
    time = datetime.date.today().isoformat()
    db.add_script(creators, urls_joined, duration, time)
    db.commit()
    db.con.close()

def is_prompt_confirm():
    questions = [
        {
            'type': 'confirm',
            'message': 'Do you want to save these clips to DB?',
            'name': 'confirm',
            'default': True,
        },
    ]
    answers = prompt(questions)
    return answers['confirm']

def publish(args, confirm=True):
    URLS_FILE = args.wd / Path('./urls.txt')
    urls = URLS_FILE.read_text().split('\n')
    for u in urls:
        print(u)
    if not confirm or is_prompt_confirm():
        write_script_to_db(urls)
        update_publish_flags_db(urls)
        print(f'Published {len(urls)} clips!')
    else:
        print(f'Publishing cancelled!')

if __name__ == '__main__':
    args = {}
    args.wd = Path('./default')
    publish(args)

    #TODO: Fix mistakes in clips table
    # read pulished table and then update clips where needed