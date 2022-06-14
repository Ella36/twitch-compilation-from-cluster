#!/usr/bin/python3
import re
import datetime
from dateutil.relativedelta import relativedelta

from model.cluster import Creator

class Clip:
    def __init__(
        self,
        creator: Creator,
        url: str,
        duration: str,
        views: str,
        time: str
        ):
        self.creator = creator
        self.url = self._url(url)
        self.views = self._views(views)
        self.duration = self._duration(duration)
        self.time = self._time(time)

    def _views(self, x: str) -> int:
        # 74.7K -> 74000
        if 'k' in x.lower():
            return int(float(re.match(r'\d+\.*\d*', x)[0])*1000)
        else:
            return int(re.match(r'\d+', x)[0])

    def _url(self, x: str) -> str:
        # strip url
        # https://www.twitch.tv/cdnthe3rd/clip/WonderfulPlayfulLaptopPRChase-fa12L0MzNZ5IEG6F?filter=clips&range=30d&sort=time,0:45,45 views,14 days ago
        # https://www.twitch.tv/cdnthe3rd/clip/WonderfulPlayfulLaptopPRChase-fa12L0MzNZ5IEG6F
        return x.split('?')[0]

    def _duration(self, x: str) -> int:
        # 0:30 -> 30
        return int(re.findall(r'\d+', x)[0]) * 60 + int(re.findall(r'\d+', x)[1])

    def _time(self, x: str) -> int:
        # 2 days ago -> date in YYYY-MM-DD
        today = datetime.date.today()
        splitted = x.split()
        if len(splitted) == 1 and splitted[0].lower() == 'today':
            return str(today.isoformat())
        elif len(splitted) == 1 and splitted[0].lower() == 'yesterday':
            date = today - relativedelta(days=1)
            return str(date.isoformat())
        elif splitted[1].lower() in ['second', 'seconds', 's', 'secs']:
            date = datetime.datetime.now() - relativedelta(seconds=int(splitted[0]))
            return str(date.date().isoformat())
        elif splitted[1].lower() in ['minute', 'minutes', 'min', 'mins']:
            date = datetime.datetime.now() - relativedelta(minutes=int(splitted[0]))
            return str(date.date().isoformat())
        elif splitted[1].lower() in ['hour', 'hours', 'hr', 'hrs', 'h']:
            date = datetime.datetime.now() - relativedelta(hours=int(splitted[0]))
            return str(date.date().isoformat())
        elif splitted[1].lower() in ['day', 'days', 'd']:
            date = today - relativedelta(days=int(splitted[0]))
            return str(date.isoformat())
        elif splitted[1].lower() in ['wk', 'wks', 'week', 'weeks', 'w']:
            # Add "Last week catch"
            n = splitted[0]
            if n.lower() == "last":
                n = 1
            date = today - relativedelta(weeks=int(n))
            return str(date.isoformat())
        elif splitted[1].lower() in ['mon', 'mons', 'month', 'months', 'm']:
            # Add "Last month"
            n = splitted[0]
            if n.lower() == "last":
                n = 1
            date = today - relativedelta(months=int(n))
            return str(date.isoformat())
        elif splitted[1].lower() in ['yrs', 'yr', 'years', 'year', 'y']:
            # Add "Last year"
            n = splitted[0]
            if n.lower() == "last":
                n = 1
            date = today - relativedelta(years=int(n))
            return str(date.isoformat())
        else:
            print(f'ERROR: Wrong Argument Format {x}')
            return str(today.isoformat())
