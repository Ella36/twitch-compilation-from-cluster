#!/usr/bin/python3
import operator
from functools import reduce
from dataclasses import dataclass


@dataclass
class Creator:
    name: str
    weight: str = 1000

    def __post_init__(self):
        self.name = self.name.lower()

class Cluster():
    def __init__(self, name: str, description: str, creators: list):
        self.name = name
        self.description = description
        self.creators = creators

    def __post_init__(self):
        self.name = self.name.lower()
    
    @property
    def names(self):
        return [x.name for x in self.creators]

class Clusters():
    def __init__(self, clusters: list):
        self.clusters = clusters
    
    def by_name(self, name):
        return list(filter(lambda c: c.name == name, self.clusters))[0]

    @property
    def creators(self):
        return reduce(operator.add, [c.creators for c in self.clusters])

CLUSTERS  = Clusters([
    Cluster(
        'cluster_test',
        'for_testing',
        [ 
            Creator('turk'),
        ]
    ),
    Cluster(
        'cluster_test2',
        'for_testing2',
        [ 
            Creator('mewnfare'),
        ]
    ),
    Cluster(
        'asians',
        'subreddit r/twitchasians',
        [ 
            Creator('ahra'),
            Creator('ariasaki'),
            Creator('berry0314'),
            Creator('canahry'),
            Creator('hyoon'),
            Creator('kiaraakitty'),
            Creator('leesherwhy'),
            Creator('meowko'),
            Creator('mvngokitty'),
            Creator('sooflower'),
            Creator('sorammmm'),
            Creator('strawberrybunni'),
            Creator('supcaitlin'),
            Creator('viptoriaaa'),
            Creator('woohankyung'),
            Creator('yeonari'),
            Creator('yuggie_tv'),
        ]
    ),
])