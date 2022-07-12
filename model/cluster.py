#!/usr/bin/env python
import operator
from functools import reduce


class Creator:
    def __init__(self, name: str):
        self.name = name.lower()

class Cluster:
    def __init__(self, name: str, description: str, creators: list):
        self.name = name.lower()
        self.description = description
        self.creators = creators

    def __post_init__(self):
        assert all(isinstance(cluster, Creator) for cluster in self.creators)

    @property
    def names(self):
        return [x.name for x in self.creators]


class Clusters():
    def __init__(self, clusters: list):
        self.clusters = clusters
    
    def by_name(self, name):
        return list(filter(lambda c: c.name == name, self.clusters))[0]

    def __post_init__(self):
        assert all(isinstance(cluster, Cluster) for cluster in self.clusters)


    @property
    def creators(self):
        return reduce(operator.add, [c.creators for c in self.clusters])