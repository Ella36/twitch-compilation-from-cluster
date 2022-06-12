#!/usr/bin/python3
from regex import W


class Creator():
    def __init__(self, name, weight=1000):
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
    'Cyan - Popular NA FPS',
    [ 
        Creator('DrLupo'),
        Creator('WARDELL'),
        Creator('TenZ'),
        Creator('Subroza'),
        Creator('ScreaM'),
        Creator('Hiko'),
        Creator('Nadeshot'),
        Creator('Crowder'),
        Creator('SypherPK'),
        Creator('Clix'),
        Creator('Loeya'),
        Creator('GD_booya'),
        Creator('Replays'),
        Creator('TeePee'),
        Creator('AdinRoss'),
        Creator('NICKMERCS'),
        Creator('TimTheTatman'),
        Creator('scump'),
        Creator('AussieAntics'),
        Creator('Ninja'),
        Creator('Fazeblaze'),
        Creator('zombs'),
        Creator('its_iron'),
        Creator('Swagg'),
        Creator('Symfuhny'),
        Creator('Syndicate'),
        Creator('Aydan'),
    ]
)

CLUSTER2 = Cluster(
    'cluster2',
    'Purple - Popular NA FPS',
    [ 
        Creator('shroud'),
        Creator('summit1g'),
        Creator('gladd'),
        Creator('cdnthe3rd'),
        Creator('chocotaco'),
        Creator('lvndmark'),
        Creator('smoke'),
        Creator('deadlysob'),
        Creator('lirik'),
        Creator('Kitboga'),
    ]
)

CLUSTER3 = Cluster(
    'cluster3',
    'Cyan2',
    [ 
        Creator('mitr0'),
        Creator('SnaggyMo'),
        Creator('Silky'),
        Creator('Fresh'),
        Creator('x2Twins'),
        Creator('Reetlol'),
        Creator('scoped'),
        Creator('Im_Dontai'),
        Creator('UnknownxArmy'),
        Creator('blake'),
        Creator('EpikWhale'),
        Creator('Bugha'),
        Creator('benjyfishy'),
        Creator('fazeapex'),
        Creator('brucedropemoff'),
        Creator('mongraal'),
        Creator('wolfiez'),
    ]
)

CLUSTER4 = Cluster(
    'cluster4',
    'Pink1',
    [ 
        Creator('Sykkuno'),
        Creator('PointCrow'),
        Creator('CallMeCarsonLIVE'),
        Creator('TinaKitten'),
        Creator('starsmitten'),
        Creator('callmekevin'),
        Creator('aphromoo'),
        Creator('julien'),
        Creator('pointcrow'),
        Creator('cardboard_cowboy'),
        Creator('ash_on_lol'),
        Creator('itshafu'),
        Creator('5uppp'),
        Creator('39daph'),
        Creator('pointcrow'),
        Creator('jccaylen'),
        Creator('pointcrow'),
        Creator('ludwig'),
    ]
)

CLUSTER5 = Cluster(
    'cluster5',
    'Pink2',
    [ 
        Creator('ariasaki'),
        Creator('atrioc'),
        Creator('baboabe'),
        Creator('bnans'),
        Creator('fuslie'),
        Creator('grabsmolders'),
        Creator('itsryanhiga'),
        Creator('mang0'),
        Creator('masayoshi'),
        Creator('natsumiii'),
        Creator('peterparkTV'),
        Creator('pokimane'),
        Creator('qtcinderella'),
        Creator('quarterjade'),
        Creator('scarra'),
        Creator('stevesuptic'),
        Creator('xchocobars'),
        Creator('yvonnie'),
        Creator('lilypichu'),
    ]
)

CLUSTER6 = Cluster(
    'cluster6',
    'Yellow',
    [ 
        Creator('loltyler1'),
        Creator('doublelift'),
        Creator('rekkles'),
        Creator('faker'),
        Creator('kingeorge'),
        Creator('tfue'),
        Creator('ops1x'),
        Creator('s0mcs'),
        Creator('gosu'),
        Creator('jankos'),
    ]
):W


CLUSTER7 = Cluster(
    'cluster7',
    'Purple2',
    [ 
        Creator('sodapoppin'),
        Creator('xqcow'),
        Creator('greekgodx'),
        Creator('trainwreckstv'),
        Creator('nmplol'),
        Creator('nymn'),
        Creator('pokelawls'),
        Creator('mizkif'),
        Creator('clintstevens'),
        Creator('asmongold'),
        Creator('cohhcarnage'),
        Creator('mitchjones'),
        Creator('esfandtv'),
        Creator('moonmoon'),
        Creator('zackrawrr'),
        Creator('quin69'),
        Creator('richwcampbell'),
    ]

CLUSTER8 = Cluster(
    'cluster8',
    'Green',
    [ 
        Creator('Markiplier'),
        Creator('CaptainSparklez'),
        Creator('LDShadowLady'),
        Creator('Thunder1408'),
        Creator('tommyinnit'),
        Creator('GeorgeNotFound'),
        Creator('QuackityHQ'),
        Creator('BadBoyHalo'),
        Creator('CaptainPuffy'),
        Creator('4freakshow'),
        Creator('4freakshow'),
        Creator('WilburSoot'),
        Creator('JustaMinx'),
        Creator('DropsByPonk'),
        Creator('HBomb94'),
        Creator('RanbooLive'),
        Creator('CrankGameplays'),
        Creator('awesamdude'),
        Creator('Punz'),
        Creator('Fundy'),
        Creator('Snapsnap'),
        Creator('Nihachu'),
        Creator('karljacobs'),
        Creator('ConnorEatsPants'),
        Creator('Philza'),
    ]
)

CLUSTER9 = Cluster(
    'cluster9',
    'Darkblue french',
    [ 
        Creator('Sardoche'),
        Creator('JeelTV'),
        Creator('chesscomfr'),
        Creator('Doigby'),
        Creator('The8BitDrummer'),
        Creator('Tonton'),
        Creator('Jirayalecochon'),
        Creator('JeanMassietAccropolis'),
        Creator('AlphaCast'),
        Creator('Skyyart'),
        Creator('AntoineDanielLive'),
        Creator('Ponce'),
        Creator('SkyrrozTV'),
        Creator('JeelTV'),
        Creator('chowh1'),
        Creator('1PVCS'),
        Creator('JLBichouu'),
        Creator('JLTomy'),
        Creator('LeBouseuh'),
        Creator('Gotaga'),
        Creator('Valouzz'),
        Creator('SackziTV'),
        Creator('Terracid'),
    ]
)

CLUSTER10 = Cluster(
    'cluster10',
    'Darkblue 2 french',
    [ 
        Creator('lestream'),
        Creator('drfeelgood'),
        Creator('fantabobshow'),
        Creator('laink'),
        Creator('xari'),
        Creator('domingo'),
        Creator('locklear'),
        Creator('laink'),
        Creator('corobizar'),
        Creator('alderiate'),
        Creator('shaunz'),
        Creator('solary'),
        Creator('zerator'),
        Creator('Joueur_du_grenier'),
        Creator('SolaryHS'),
        Creator('Maghla'),
        Creator('LittleBigWhale'),
        Creator('Altair'),
        Creator('ImSoFresh'),
        Creator('robert87000'),
    ]
)

CLUSTERS = Clusters([CLUSTER1, CLUSTER2]) 

if __name__ == '__main__':
    print('Verifying clusters for any mistakes')
    for cluster in CLUSTERS.clusters:
        names = cluster.names
        # Assert if names are unique
        assert(len(names) == len(set(names)))
    print('No mistakes found')