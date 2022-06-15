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

class Cluster:
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
        Cluster(
        'league',
        'NA Orange League atlas 2022-01',
        [ 
            Creator('aphromoo'),
            Creator('bjergsenlol'),
            Creator('bobginxd'),
            Creator('broxah'),
            Creator('caedrel'),
            Creator('caps'),
            Creator('caps'),
            Creator('doublelift'),
            Creator('dzukill'),
            Creator('gosu'),
            Creator('imaqtpie'),
            Creator('imls'),
            Creator('iwilldominate'),
            Creator('jankos'),
            Creator('lol_nemesis'),
            Creator('loltyler1'),
            Creator('midbeast'),
            Creator('nightblue'),
            Creator('pobelter'),
            Creator('quantum'),
            Creator('ratirl'),
            Creator('sanchovies'),
            Creator('sirhcez'),
            Creator('sneakylol'),
            Creator('solarbacca'),
            Creator('solorenektononly'),
            Creator('tarzaned'),
            Creator('tfblade'),
            Creator('thebausffs'),
            Creator('tobiasfate'),
            Creator('trick2g'),
        ]
    ),
        Cluster(
        'vtuber',
        'vtoobers',
        [ 
            Creator('ironmouse'),
            Creator('shylily'),
            Creator('nihmune'),
            Creator('baoo'),
            Creator('projektmelody'),
            Creator('silvervale'),
            Creator('yuzu'),
            Creator('momo'),
            Creator('snuffy'),
            Creator('nyanners'),
            Creator('harukakaribu'),
            Creator('veibae'),
            Creator('remuchii'),
            Creator('misu'),
            Creator('filian'),
            Creator('zentreya'),
            Creator('elly_vt'),
            Creator('laynalazar'),
            Creator('remuchii'),
        ]
    ),
    Cluster(
        'pinktuber',
        'NA pink vtuber atlas',
        [ 
            Creator('anny'),
            Creator('baoo'),
            Creator('cdawgva'),
            Creator('harukakaribu'),
            Creator('ironmouse'),
            Creator('lordaethelstan'),
            Creator('nihmune'),
            Creator('nyanners'),
            Creator('projektmelody'),
            Creator('shylily'),
            Creator('silvervale'),
            Creator('saruei'),
            Creator('apricot'),
            Creator('chibidoki'),
            Creator('snuffy'),
            Creator('thean1meman'),
            Creator('trashtastepodcast'),
            Creator('veibae'),
            Creator('zentreya'),
        ]
    ),
    Cluster(
        'na_camgirls',
        'NA sfw camgirls - DarkGreen Atlas + hottub streamers',
        [ 
            Creator('adrianachechik_'),
            Creator('alinity'),
            Creator('amouranth'),
            Creator('evaanna'),
            Creator('faith'),
            Creator('gogogirl_tv'),
            Creator('ibabyrainbow'),
            Creator('kandyland'),
            Creator('kiaraakitty'),
            Creator('kyootbot'),
            Creator('leynainu'),
            Creator('littlelianna'),
            Creator('melina'),
            Creator('miamalkova'),
            Creator('missmercyy'),
            Creator('spoopykitt'),
            Creator('taylor_jevaux'),
        ]
    ),
])