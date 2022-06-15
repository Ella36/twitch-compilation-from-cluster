#!/usr/bin/python3
from model.cluster import Creator
import pandas as pd
import unicodedata
import string


class Clip:
    def __init__(
        self,
        creator: Creator = None,
        request: dict = None,
        game: str = None,
        row: pd.Series = None,
        from_row: bool = False,
        ):
        if not from_row:
            self.creator: Creator = creator
            #self.broadcaster_id = request['broadcaster_id']
            #self.creator_id  = request['creator_id']
            #self.embed_url = request['embed_url']
            #self.video_id  = request['video_id']
            #self.broadcaster_name: str = request['broadcaster_name']
            self.created_at: str = self._created_at(request['created_at'])
            self.clipper_name: str = request['creator_name']
            self.duration: float = request['duration']
            self.game_id: str = request['game_id']
            self.game: str = game
            self.language: str = self._language(request['language'])
            self.thumbnail_url: str = request['thumbnail_url']
            self.title: str = request['title']
            self.url: str = request['url']
            self.view_count: int = request['view_count']
            #self.to_string = to_string
        else:
            self.creator = Creator(row.creator)
            self.game = row.game
            self.clipper_name = row.clipper_name
            self.game_id = row.game_id
            self.language = row.language
            self.view_count = row.view_count
            self.duration = row.duration
            self.title = row.title
            self.url = row.url
            self.created_at = row.created_at

    def to_string(self):
        return f'{self.creator.name:20} {self.game:10} {self.language:3} {self.view_count:7} {self.duration:5} {self.title} {self.created_at}'

    def _created_at(self, x: str) -> str:
        return x.split('T')[0]

    def _language(self, x: str) -> str:
        return x if x!='en-gb' else 'en'

def str_to_filename(str):
    validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleanedFilename = unicodedata.normalize('NFKD', str).encode('ASCII', 'ignore')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)

class Element:
    def __init__(
        self,
        clip: Clip,
        order: int,
        download: bool = False,
        error: bool = False,
        ):
        self.clip: Clip = clip
        self.order: int = order
        self.download: bool = download
        self.error: bool = error
    
    @property
    def filename(self):
        return str_to_filename(f"{self.order:03d}-{self.clip.creator.name}-{self.clip.view_count}-{self.clip.game_id}")+".mp4"

    @property
    def url(self):
        return self.clip.url


import pickle
from pathlib import Path

class Compilation:
    def __init__(
        self,
    ):
        self.list = []
    
    def __iter__(self):
        for element in self.list:
            yield element

    def dump(self, file: Path):
        with file.open('wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(self, filepath: Path):
        with filepath.open('rb') as f:
            compilation = pickle.load(f)
        return compilation

    def clips_in_order(self):
        return self.list.sort(key=lambda e: e.order)

    def add(self, clip: Clip):
        # TODO: remove download, error?
        new_element = Element(clip, len(self.list)+1, download=False, error=False)
        self.list.append(new_element)