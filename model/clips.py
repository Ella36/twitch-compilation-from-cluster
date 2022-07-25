#!/usr/bin/env python
import unicodedata
import string
from pathlib import Path
import re
import json
from types import SimpleNamespace

import pandas as pd
from InquirerPy import prompt

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
            self.thumbnail_url = row.thumbnail_url

    def __eq__(self, other):
        if not isinstance(other, Clip):
            return False
        return self.url == other.url

    def __ne__(self, other):
        if not isinstance(other, Clip):
            return True
        return self.url != other.url


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
        return self.wd / Path('./download') / Path(str_to_filename(f"{self.order:03d}-{self.clip.creator.name}-{self.clip.view_count}-{self.clip.game_id}-{self.clip.title}")+".mp4")

    @property
    def filename_input(self):
        return self.wd / Path('./input') / Path(str_to_filename(f"{self.order:03d}-{self.clip.creator.name}-{self.clip.view_count}-{self.clip.game_id}-{self.clip.title}")+".mp4")

    @property
    def filename_build_ts(self):
        return self.wd / Path('./build') / Path(str_to_filename(f"{self.order:03d}-{self.clip.creator.name}-{self.clip.view_count}-{self.clip.game_id}-{self.clip.title}")+".ts")

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
                print("\tRemoving clip from disk:\n\t\t{f.name}")
                find[0].unlink()
            elif len(find) > 1:
                print(f"\tERROR: CANT UPDATE MULTIPLE FOUND:\n\t\t{[x.name for x in find]}")
        else:
            print("\tRemoving clip from disk:\n\t\t{f.name}")
            f.unlink()


import pickle
from pathlib import Path

class Compilation:
    def __init__(
        self,
        wd: Path = Path('.'),
        filename: str = 'compilation.pkl',
        clips: list = [],
        project: str = 'untitled',
    ):
        self.list = []
        self.wd = wd
        self.filename = filename
        self.project = project
        self.pid = None
        if len(clips) > 0:
            for clip in clips:
                self.add(clip)
    
    def __post_init__(self):
        self.sync_compilation_with_disk()
    
    def __iter__(self):
        for element in self.list:
            yield element

    def to_json(self):
        # compilation to json
        dict = {}
        dict["project"] = self.project
        dict["wd"] = str(self.wd)
        dict["n"] = len(self.list)
        clips = []
        for e in self.list:
            # Do not add if clip has encountered error
            if e.error:
                continue
            element = {}
            element["download"] = e.download
            element["error"] = e.error
            c = e.clip
            element["url"] = c.url
            element["created_at"] = c.created_at
            element["game_id"] = c.game_id
            element["game"] = c.game
            element["creator"] = c.creator.name
            element["language"] = c.language
            element["thumbnail_url"] = c.thumbnail_url
            element["title"] = c.title
            element["duration"] = c.duration
            element["view_count"] = c.view_count
            clips.append(element)
        dict["clips"] = clips
        out = json.dumps(dict, default=str, indent=2)
        return out
        
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

    def sync_compilation_with_disk(self, is_confirm_with_prompt=True):
        def _prompt_confirm(step: str):
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
        def _remove_elements_with_errors_from_disk(elements):
            for e in [e for e in elements if e.error]:
                f = Path(e.filename)
                if not f.exists():
                    find = list(f.parent.glob(f"*{e.filename_stem_without_order}*"))
                    if len(find) == 1:
                        print(f"\tFound(ish) on disk:\n\t\t{find[0].name}")
                        print(f"\Remove file with error!\n\t\t{f.name}")
                        if not is_confirm_with_prompt or _prompt_confirm("Remove file"):
                            f.unlink()
                            e.download = False
                    elif len(find) > 1:
                        print(f"\tSearching glob:\n\t\t{find}")
                        print(f"\tERROR: CANT REMOVE MULTIPLE FOUND:\n\t\t{[x.name for x in find]}")
                    else:
                        print(f"\tNot found!")
                else:
                    if not is_confirm_with_prompt or _prompt_confirm("Remove file"):
                        f.unlink()
        def _find_element_on_disk_and_rename_if_needed(e: Element):
            print(f"{e.filename_stem_without_order}")
            f = Path(e.filename)
            if Path(str(f) + ".part").exists():
                print(f"\tFound .part on disk:\n\t\t{f.name}")
                e.download = False
                return
            if not f.exists():
                find = list(f.parent.glob(f"*{e.filename_stem_without_order}*"))
                if len(find) == 1:
                    print(f"\tFound(ish) on disk:\n\t\t{find[0].name}")
                    e.download = True
                    # CHECK FOR .PART
                    suffix = ".part" if re.search(r'\.part$', str(find[0])) else ""
                    f = Path(str(f) + suffix)
                    print(f"\tRenaming!\n\t\t{f.name}")
                    # Prompt to rename
                    # if _prompt_confirm("Rename file"):
                    find[0].rename(f)
                elif len(find) > 1:
                    print(f"\tSearching glob:\n\t\t{find}")
                    print(f"\tERROR: CANT UPDATE MULTIPLE FOUND:\n\t\t{[x.name for x in find]}")
                else:
                    print(f"\tNot found!")
            else:
                print(f"\tFound on disk:\n\t\t{f.name}")
                e.download = True
        def _remove_clips_that_are_not_present(elements):
            download_dir = self.wd / Path('./download')
            find = list(download_dir.glob(f"*.mp4"))
            filenames = [e.filename for e in elements]
            print(f"Looking for clips that dont belong")
            for f in find:
                if not (f in filenames ):
                    print(f"\tClip found on disk not in df:\n\t\t{f.name}")
                    if not is_confirm_with_prompt or _prompt_confirm("Remove file"):
                        f.unlink()
        _remove_elements_with_errors_from_disk(self.list)
        for element in self.list:
            _find_element_on_disk_and_rename_if_needed(element)
        _remove_clips_that_are_not_present(self.list)

    def order_clips(self):
        self.list.sort(key=lambda e: e.order)
        return self

    def add(self, clip: Clip):
        new_element = Element(clip, len(self.list)+1, wd=self.wd, download=False, error=False)
        self.list.append(new_element)