#!/usr/bin/python3
from dataclasses import dataclass, field

from .cluster import Cluster


class Projects():
    def __init__(self, projects: list):
        self.projects = projects
    
    def by_name(self, name):
        return list(filter(lambda c: c.name == name, self.projects))[0]

def are_elements_of_type(_list: str, _type) -> bool: 
    return len(_list) == 0 \
        or all(isinstance(e, _type) for e in _list)

@dataclass
class Project:
    name: str = "default"
    description: str = "no description added"
    title: str = "untitled"
    playlist_title: str = "untitled"
    days: int = 30
    n_per_month: int = 1 # videos per month
    duration: int = 600
    categories: list = field(default_factory=list)
    clip_ids: list = field(default_factory=list)
    clusters: list = field(default_factory=list)
    creators: list = field(default_factory=list)
    game_ids: list = field(default_factory=list)
    lang: str = 'en'
    resolution: str = '720'
    is_ok_already_published: bool = False
    skip_draw: bool = True
    single: bool = False # compilation of 1 single clip
    is_active: bool = True # compilation of 1 single clip
    youtube_category_id: str = "20" # Gaming 20,  Entertainment 24, People Blogs 22,

    def __post_init__(self):
        self.name: str = self.name.lower()
        self.interval: int = 30 // self.n_per_month
        assert are_elements_of_type(self.game_ids, str)
        assert are_elements_of_type(self.creators, str)
        assert are_elements_of_type(self.clip_ids, str)
        assert are_elements_of_type(self.clusters, str)
        assert are_elements_of_type(self.categories, str)