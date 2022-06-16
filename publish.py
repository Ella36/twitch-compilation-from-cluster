#!/usr/bin/python3
from pathlib import Path
import datetime

from model.mydb import Mydb
from model.clips import Compilation

def write_compilation_to_db(compilation):
    creators = ','.join([e.clip.creator.name for e in compilation])
    urls = ','.join([e.clip.url for e in compilation])
    duration = ','.join([str(e.clip.duration) for e in compilation])
    time = datetime.date.today().isoformat()
    db = Mydb()
    db.add_compilation(creators, urls, duration, time, compilation.project)
    db.set_published_from_compilations()
    db.commit()
    db.con.close()

def publish(args):
    compilation = Compilation.load(args.wd)
    write_compilation_to_db(compilation)
    print(f'Published {len(compilation.list)} clips!')

if __name__ == '__main__':
    args = {}
    args.wd = Path('./default')
    publish(args)