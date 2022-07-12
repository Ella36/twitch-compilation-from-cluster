#!/usr/bin/python3
from model.cluster import Creator, Cluster, Clusters
from model.project import Project, Projects


CLUSTERS  = Clusters([
    Cluster(
        'cluster_sample',
        'sample for testing',
        [ 
            Creator('nymn'),
            Creator('willneff'),
            Creator('esfandtv'),
            Creator('nmplol'),
        ],
    ),
])

PROJECTS = Projects([
    Project(
        name='cluster_sample_30d',
        description='Sample cluster clips',
        title='Sample',
        playlist_title='sample playlist',
        days=30,
        n_per_month=2,
        is_active=True,
        skip_draw=False,
        resolution='360',
        duration=60,
        youtube_category_id = "24", # Gaming 20,  Entertainment 24, People Blogs 22,
        single=False, 
        clusters=[
            ('cluster_sample'),
        ],
    ),
])
