#!/usr/bin/python3
import unicodedata
import string
from pathlib import Path

import pandas as pd

from model.cluster import Creator


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
        return f'{self.creator.name:10} {self.game:10} {self.language:3} {self.view_count:6} {self.duration:5} {self.title} {self.created_at}'

    def _created_at(self, x: str) -> str:
        return x.split('T')[0]

    def _language(self, x: str) -> str:
        return x if x!='en-gb' else 'en'

def str_to_filename(str):
    valid_filename_chars = "-_.() {0}{1}".format(string.ascii_letters, string.digits)
    cleanedFilename = unicodedata.normalize('NFKD', str).encode('ASCII', 'ignore').decode('ascii')
    return ''.join(c for c in cleanedFilename if c in valid_filename_chars)

class Element:
    def __init__(
        self,
        clip: Clip,
        order: int,
        download: bool = False,
        error: bool = False,
        wd: Path = Path('.'),
        ):
        self.clip: Clip = clip
        self.order: int = order
        self.download: bool = download
        self.error: bool = error
        self.wd: Path = wd
        
    def to_string(self):
        return f"{self.order} {self.filename_stem_without_order} DL?{self.download} ERR?{self.error} Clip:{self.clip.to_string()}"
    
    @property
    def filename(self):
        return self.wd / Path('./download') / str_to_filename(f"{self.order:03d}-{self.clip.creator.name}-{self.clip.view_count}-{self.clip.game_id}")+".mp4"

    @property
    def filename_stem_without_order(self):
        return str_to_filename(f"{self.clip.creator.name}-{self.clip.view_count}-{self.clip.game_id}")

    @property
    def url(self):
        return self.clip.url

    def remove_from_disk(self):
        # Remove file
        f = Path(self.filename)
        if not f.exists():
            find = list(f.parent.glob(f"*{self.filename_stem_without_order}*"))
            if len(find) == 1:
                print("Removing clip from disk:\t\n{f}")
                find[0].unlink()
            elif len(find) > 1:
                print(f"ERROR: CANT UPDATE MULTIPLE FOUND:\n\t{[x.name for x in find]}")
        else:
            print("Removing clip from disk:\t\n{f}")
            f.unlink()

    def update_order_to_disk(self) -> bool:
        # Update order if wrong
        f = Path(self.filename)
        if not f.exists():
            find = list(f.parent.glob(f"*{self.filename_stem_without_order}*"))
            if len(find) == 1:
                find[0].rename(f.filename)
                return True
            elif len(find) > 1:
                print(f"ERROR: CANT UPDATE MULTIPLE FOUND:\n\t{[x.name for x in find]}")
                return False
        return True

import pickle
from pathlib import Path

class Compilation:
    def __init__(
        self,
        wd: Path = Path('.'),
        filename: str = 'compilation.pkl',
        clips: list = [],
    ):
        self.list = []
        self.wd = wd
        self.filename = filename
        if len(clips) > 0:
            for clip in clips:
                self.add(clip)
    
    def __post_init__(self):
        self.update_compilation_from_disk()
    
    def __iter__(self):
        for element in self.list:
            yield element

    def to_string(self):
        out = f'Compilation contains {len(self.list)}'
        for clip in self.list:
            out += f"\n\t{clip.to_string()}"
        return out

    def dump(self, path: Path):
        with (path / self.filename).open('wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Path):
        filename = 'compilation.pkl'
        with (path / filename).open('rb') as f:
            compilation = pickle.load(f)
        return compilation

    def update_compilation_from_disk(self):
        list_copy = self.list[:]
        for element in list_copy:
            # Update order
            if not element.update_order_to_disk():
                # Can't find on disk
                if element.download:
                    # Download flag set, but not present
                    element.remove_from_disk()
                    self.list.remove(element)
            if element.error:
                # Remove if error
                element.remove_from_disk()
                self.list.remove(element)

    def clips_in_order(self):
        return self.list.sort(key=lambda e: e.order)

    def add(self, clip: Clip):
        # TODO: remove download, error?
        new_element = Element(clip, len(self.list)+1, download=False, error=False)
        self.list.append(new_element)