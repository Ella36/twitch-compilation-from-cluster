#!/usr/bin/python3
import toml

from model.cluster import Creator, Cluster, Clusters
from model.project import Project, Projects

clusters_toml = toml.load("./cfg/clusters.toml")

clusters = []
for name, cluster_info in clusters_toml.items():
    cluster = Cluster(
        name,
        cluster_info.get('description', ''),
        [Creator(creator) for creator in cluster_info['creators']],
    )
    clusters.append(cluster)
CLUSTERS = Clusters(clusters)

projects_toml = toml.load("./cfg/projects.toml")

projects = []
for name, project_info in projects_toml.items():
    project = Project(
        name=name,
        description=project_info.get('description', ''),
        title=project_info.get('title', 'untitled'),
        playlist_title=project_info.get('playlist_title', 'untitled'),
        days=project_info.get('days', 30),
        n_per_month=project_info.get('n_per_month', 1),
        duration=project_info.get('duration', 600),
        categories=project_info.get('categories', []),
        clip_ids=project_info.get('clip_ids', []),
        clusters=project_info.get('clusters', []),
        creators=project_info.get('creators', []),
        game_ids=project_info.get('game_ids', []),
        lang=project_info.get('lang', 'en'),
        resolution=project_info.get('resolution', '720'),
        is_ok_already_published=project_info.get(
            'is_ok_already_published', False),
        skip_draw=project_info.get('skip_draw', True),
        draw_clip_title_only=project_info.get('draw_clip_title_only', False),
        single=project_info.get('single', False),
        is_active=project_info.get('is_active', True),
        youtube_category_id=project_info.get('youtube_category_id', '20')
    )
    projects.append(project)
PROJECTS = Projects(projects)
