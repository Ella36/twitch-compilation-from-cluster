#!/usr/bin/python3
# Select clips from creators
# Keep in mind view count, duration to till 10mins and avoid duplicates
import pandas as pd
from pathlib import Path
import re
import random

URLS = Path('./urls')

# Select creators
creators = ['gladd', 'summit1g', 'shroud', 'smoke', 'cdnthe3rd']

def parse_int(x):
    # 18.2K views
    # 28 views
    if 'k' in x.lower():
        return int(float(re.match(r'\d+\.*\d*', x)[0])*1000)
    else:
        return int(re.match(r'\d+', x)[0])


clips_info = []
# Read data
for creator in creators:
    clip_info_file = URLS / Path(creator+'.txt')
    clip_info = pd.read_csv(
        clip_info_file,
        delimiter=',',
        names=['url','duration','views','interval'],
        )
    # Convert to usable
    clip_info['views'] = clip_info['views'].apply(parse_int)
    clip_info['duration'] = clip_info['duration'].apply(
        lambda x: int(re.findall(r'\d+', x)[0]) * 60 + int(re.findall(r'\d+', x)[1]))
    clip_info['creator'] = creator
    clips_info.append(clip_info)

# Concatenate
df_clip_info = pd.concat(clips_info, axis=0)

# Select URLs
# Rotate through each creator, select highest viewed clip
df_clip_info.sort_values(by=['views','duration'])
df = df_clip_info
df['views'].describe()
urls = []
views = []
max_duration = 610
duration = 0
for creator in creators*100:
    for idx, row in df.iterrows():
        if row.creator != creator:
            continue
        if row.url in urls:
            continue
        if row.duration + duration > max_duration:
            continue
        # Add
        urls.append(row.url)
        views.append(row.views)
        duration += row.duration
        break

print(duration)
print(urls)

# Move 3 clips with highest views to the top
url_sorted = []

most_views = max(views)
idx = views.index(most_views)
views.remove(most_views)
url = urls.pop(idx)
url_sorted.append(url)

most_views = max(views)
idx = views.index(most_views)
views.remove(most_views)
url = urls.pop(idx)
url_sorted.append(url)

most_views = max(views)
idx = views.index(most_views)
views.remove(most_views)
url = urls.pop(idx)
url_sorted.append(url)

random.shuffle(urls)
url_sorted += urls

Path('urls.txt').write_text('\n'.join(url_sorted))
