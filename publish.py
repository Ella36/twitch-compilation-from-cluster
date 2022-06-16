#!/usr/bin/python3
from pathlib import Path
import datetime

from InquirerPy import prompt

from model.mydb import Mydb


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
    db.add_compilation(creators, urls_joined, duration, time)
    db.set_published_from_compilations()
    db.commit()
    db.con.close()

def publish(args, confirm=True):
    URLS_FILE = args.wd / Path('./urls.txt')
    urls = URLS_FILE.read_text().split('\n')
    write_script_to_db(urls)
    print(f'Published {len(urls)} clips!')

if __name__ == '__main__':
    args = {}
    args.wd = Path('./default')
    publish(args)