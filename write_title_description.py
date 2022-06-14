#!/usr/bin/python3
from pathlib import Path

from InquirerPy import prompt

from db.mydb import Mydb

def write():
    TIME = Path('./time.txt')
    text = TIME.read_text().strip().split('\n')
    description = ''
    # Description
    creators = []
    for t in text:
        seconds, creator, title = t.split(';;')
        creators.append(creator)
        seconds = f'{int(seconds)//60:02d}:{int(seconds)%60:02d}'
        creator_url = f'https://twitch.tv/{creator}'
        description += """{} {:43s} {}\n""".format(seconds, creator_url, title)
    # Title
    creators_most_important = list(set(creators))
    script_number = last_index()
    if len(creators_most_important) == 1:
        title = """Twitch Compilation #{0:03d} {1})""".format(script_number, creators_most_important[0])
    elif len(creators_most_important) == 2:
        title = """Twitch Compilation #{0:03d} {1} {2}""".format(script_number, creators_most_important[0], creators_most_important[1])
    else:
        title = """Twitch Compilation #{0:03d} ({1}, {2}, ...)""".format(script_number, creators_most_important[0], creators_most_important[1])
    out = title + '\n\n' + description
    print(out)
    with Path('./title.txt').open("w+") as f:
        f.write(out)

def last_index() -> int:
        db = Mydb()
        id = db.select_latest_script_number()
        db.commit()
        db.con.close()
        return id

if __name__ == '__main__':
    write()