#!/usr/bin/python3
from pathlib import Path
import time
import argparse

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options

CLUSTER = Path('./cluster')
URLS = Path('./urls')

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

def find_creator_interval_urls(creator='mewnfare', interval='30d'):

    driver.get(f'https://www.twitch.tv/{creator}/clips?filter=clips&range={interval}')

    time.sleep(5)

    content = driver.page_source
    soup = BeautifulSoup(content, features="lxml")
    main_panel = soup.find("main")
    scrollable_area = main_panel.find("div", {"class": "root-scrollable scrollable-area"})
    scroll_list = scrollable_area.find("div", {"class": "simplebar-scroll-content"})
    links = scroll_list.findAll('a', {"data-a-target": "preview-card-image-link"})

    clip_info = []
    for l in links:
        rl = l.get('href')
        if not "/clip/" in rl:
            continue
        url = "https://www.twitch.tv" + rl
        media_stats = l.select('div[class*="tw-media-card-stat"]')
        duration = media_stats[0].text
        views = media_stats[1].text
        time_ago = media_stats[2].text
        clip_info.append(f'{url},{duration},{views},{time_ago}')

    print(f'Found: {len(clip_info)} clips!')
    (URLS / f'{creator}.txt').write_text('\n'.join(clip_info))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("cluster", help="clusterfile with name(s) of twitch channel (creator)")
    parser.add_argument("interval", help="7d or 30d")
    args = parser.parse_args()
    with open(CLUSTER / Path(args.cluster+'.txt'), 'r') as f:
        creators = f.readlines()
    for creator in creators:
        creator = creator.strip()
        print(creator)
        find_creator_interval_urls(creator=creator, interval=args.interval)