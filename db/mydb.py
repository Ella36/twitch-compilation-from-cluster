#!/usr/bin/python3
import sqlite3
import re

import datetime
from dateutil.relativedelta import relativedelta

def get_past_date(str_days_ago):
    TODAY = datetime.date.today()
    splitted = str_days_ago.split()
    if len(splitted) == 1 and splitted[0].lower() == 'today':
        return str(TODAY.isoformat())
    elif len(splitted) == 1 and splitted[0].lower() == 'yesterday':
        date = TODAY - relativedelta(days=1)
        return str(date.isoformat())
    elif splitted[1].lower() in ['hour', 'hours', 'hr', 'hrs', 'h']:
        date = datetime.datetime.now() - relativedelta(hours=int(splitted[0]))
        return str(date.date().isoformat())
    elif splitted[1].lower() in ['day', 'days', 'd']:
        date = TODAY - relativedelta(days=int(splitted[0]))
        return str(date.isoformat())
    elif splitted[1].lower() in ['wk', 'wks', 'week', 'weeks', 'w']:
        date = TODAY - relativedelta(weeks=int(splitted[0]))
        return str(date.isoformat())
    elif splitted[1].lower() in ['mon', 'mons', 'month', 'months', 'm']:
        date = TODAY - relativedelta(months=int(splitted[0]))
        return str(date.isoformat())
    elif splitted[1].lower() in ['yrs', 'yr', 'years', 'year', 'y']:
        date = TODAY - relativedelta(years=int(splitted[0]))
        return str(date.isoformat())
    else:
        return "Wrong Argument format"

class Mydb():
    def __init__(self):
        self.con = sqlite3.connect('file:clips.db?mode=rw', uri=True)
        self.cur = self.con.cursor()

    def create(self):
        self.cur.execute('''DROP table IF EXISTS clips''')
        self.cur.execute('''CREATE TABLE clips
                    (creator text, url text, duration integer, views integer, time text, published integer)''')
        self.con.commit()

    def _views(self, x):
        # 74.7K -> 74000
        if 'k' in x.lower():
            return int(float(re.match(r'\d+\.*\d*', x)[0])*1000)
        else:
            return int(re.match(r'\d+', x)[0])

    def _url(self, x):
        # strip url
        # https://www.twitch.tv/cdnthe3rd/clip/WonderfulPlayfulLaptopPRChase-fa12L0MzNZ5IEG6F?filter=clips&range=30d&sort=time,0:45,45 views,14 days ago
        # https://www.twitch.tv/cdnthe3rd/clip/WonderfulPlayfulLaptopPRChase-fa12L0MzNZ5IEG6F
        return x.split('?')[0]

    def _time(self, x):
        # 2 days ago -> date in YYYY-MM-DD
        return get_past_date(x)

    def _duration(self, x):
        # 0:30 -> 30
        return int(re.findall(r'\d+', x)[0]) * 60 + int(re.findall(r'\d+', x)[1])

    def is_url_in(self, url):
        self.cur.execute("""SELECT url FROM clips WHERE url=?""", (url,))
        return True if self.cur.fetchone() else False
    
    def add(self, creator, url, duration, views, time, published=False):
        url = self._url(url)
        if self.is_url_in(url):
            print(f'Duplicate not added:\n\t{url}')
            return
        duration = self._duration(duration)
        views = self._views(views)
        time = self._time(time)
        published = 1 if published else 0
        self.cur.execute(f"INSERT INTO clips VALUES ('{creator}', '{url}','{duration}','{views}','{time}','{published}')")
    
    def commit(self):
        self.con.commit()

if __name__ == '__main__':
    # Create table
    db = Mydb()
    db.create()
