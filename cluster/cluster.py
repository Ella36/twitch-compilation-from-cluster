#!/usr/bin/python3
class Creator():
    def __init__(self, name, weight):
        self.name = name
        self.weigth = weight

class Cluster():
    def __init__(self, name, description, creators):
        self.name = name
        self.description = description
        self.creators = creators
    
    @property
    def names(self):
        return [x.name for x in self.creators]

class Clusters():
    def __init__(self, clusters):
        self.clusters = clusters
    
    def by_name(self, name):
        return list(filter(lambda c: c.name == name, self.clusters))[0]


CLUSTER1 = Cluster(
    'cluster1',
    'Popular NA FPS',
    [ 
        Creator('shroud', 1000),
        Creator('summit1g', 1000),
        Creator('gladd', 1000),
        Creator('cdnthe3rd', 1000),
        Creator('chocotaco', 1000),
        Creator('lvndmark', 1000),
        Creator('smoke', 1000),
        Creator('deadlysob', 1000),
        Creator('lirik', 1000),
        Creator('cohhcarnage', 1000),
    ]
)

CLUSTERS = Clusters([CLUSTER1]) 

if __name__ == '__main__':
    print('Verifying clusters for any mistakes')
    assert(len(CLUSTERS) > 0)
    for cluster in CLUSTERS:
        names = cluster.names
        # Assert if names are unique
        assert(len(names) == len(set(names)))
    print('No mistakes found')