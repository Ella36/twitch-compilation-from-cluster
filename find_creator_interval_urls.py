#!/usr/bin/python3
from pathlib import Path
import time
import argparse

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options

from cluster.cluster import CLUSTERS
from db.mydb import Mydb

CLUSTER = Path("./cluster")
URLS = Path("./urls")
MYDB = Mydb()

class TwitchClipPageSeleniumDriver():
    def __init__(self):
        self.options = Options()
        self.options.headless = True

    def _find_creator_page(self, creator, interval):
        self.driver.get(f"https://www.twitch.tv/{creator}/clips?filter=clips&range={interval}")
        time.sleep(7) # Wait for element to load
        content = self.driver.page_source
        self.driver.close() # Should close as we only use 1 tab
        return content

    def _parse_clips_info(self, content):
        soup = BeautifulSoup(content, features="lxml")
        main_panel = soup.find("main")
        scrollable_area = main_panel.find("div", {"class": "root-scrollable scrollable-area"})
        scroll_list = scrollable_area.find("div", {"class": "simplebar-scroll-content"})
        preview_card_images = scroll_list.findAll("a", {"data-a-target": "preview-card-image-link"})
        is_valid_card = lambda a: True if "/clip/" in a.get("href") else False
        valid_cards = filter(is_valid_card, preview_card_images)
        def _extract_media_info(a):
            media_stats = a.select("div[class*='tw-media-card-stat']")
            return {"url": "https://www.twitch.tv" + a.get("href"),
                    "duration" : media_stats[0].text,
                    "views" : media_stats[1].text,
                    "time_ago" : media_stats[2].text,
                    }
        clip_info = list(map(_extract_media_info, valid_cards))
        return clip_info

    def find_creator_clip_info(self, creator, interval):
        try:
            self.driver = webdriver.Firefox(options=self.options)
            content = self._find_creator_page(creator, interval)
            clip_info = self._parse_clips_info(content)
        except Exception as e:
            print(e)
            self.driver.quit() # Quit if anything goes wrong
        return clip_info

def write_creator_clip_info_to_csv(creator, clip_info):
    to_csv = lambda x : f"{x['url']},{x['duration']},{x['views']},{x['time_ago']}"
    text = '\n'.join(list(map(to_csv, clip_info)))
    (URLS / f'{creator}.csv').write_text(text)

def write_creator_clip_info_to_db(creator, clip_info):
    for c in clip_info:
        MYDB.add(creator, c['url'],c['duration'],c['views'],c['time_ago'])
    MYDB.commit()

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("cluster", help="clusterfile with name(s) of twitch channel (creator)")
    parser.add_argument("interval", help="7d or 30d")
    return parser.parse_args()

if __name__ == "__main__":
    args = argparser()
    creators = CLUSTERS.by_name(args.cluster).names
    twitch_clip_page_driver = TwitchClipPageSeleniumDriver()
    for creator in creators:
        print(creator)
        clip_info = twitch_clip_page_driver.find_creator_clip_info(creator, args.interval)
        print(f"Found: {len(clip_info)} clips!")
        #write_creator_clip_info_to_csv(creator, clip_info)
        write_creator_clip_info_to_db(creator, clip_info)
    twitch_clip_page_driver.driver.quit()