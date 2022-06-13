#!/usr/bin/python3
import operator
from functools import reduce
from dataclasses import dataclass


@dataclass
class Creator:
    name: str
    weight: str = 1000

class Cluster():
    def __init__(self, name: str, description: str, creators: list):
        self.name = name
        self.description = description
        self.creators = creators
    
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

cluster1 = Cluster(
    'cluster1',
    'Cyan - Popular NA FPS',
    [ 
        Creator('DrLupo'),
        Creator('WARDELL'),
        Creator('TenZ'),
    ]
)

cluster_test = Cluster(
    'test',
    'for_testing',
    [ 
        Creator('DrLupo'),
        Creator('WARDELL'),
        Creator('TenZ'),
    ]
)

CLUSTERS = Clusters([cluster1, cluster_test]) 