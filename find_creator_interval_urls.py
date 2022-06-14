#!/usr/bin/python3
import argparse
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from model.cluster import CLUSTERS
from model.cluster import Creator
from model.clip import Clip
from db.mydb import Mydb


class TwitchClipPageSeleniumDriver():
    def __init__(self):
        self.options = Options()
        self.options.headless = True

    def _find_creator_page(self, creator: Creator, args) -> str:
        self.driver.get(f"https://www.twitch.tv/{creator.name}/clips?filter=clips&range={args.interval}")
        time.sleep(int(args.wait)) # Wait for element to load
        content = self.driver.page_source
        self.driver.close() # Should close as we only use 1 tab
        return content

    def _extract_clips(self, content: str, creator: Creator) -> list:
        soup = BeautifulSoup(content, features="lxml")
        main_panel = soup.find("main")
        scrollable_area = main_panel.find("div", {"class": "root-scrollable scrollable-area"})
        scroll_list = scrollable_area.find("div", {"class": "simplebar-scroll-content"})
        preview_card_images = scroll_list.findAll("a", {"data-a-target": "preview-card-image-link"})
        is_valid_card = lambda a: True if "/clip/" in a.get("href") else False
        valid_cards = filter(is_valid_card, preview_card_images)
        def _extract_clip_from_card(a: dict) -> Clip:
            media_stats = a.select("div[class*='tw-media-card-stat']")
            return Clip(
                    creator=creator,
                    url="https://www.twitch.tv" + a.get("href"),
                    duration=media_stats[0].text,
                    views=media_stats[1].text,
                    time=media_stats[2].text
                    )
        clips = list(map(_extract_clip_from_card, valid_cards))
        return clips

    def find_creator_clips(self, creator: Creator, args) -> list:
        try:
            self.driver = webdriver.Firefox(options=self.options)
            content = self._find_creator_page(creator, args)
            clips = self._extract_clips(content, creator)
        except Exception as e:
            print(e)
            self.driver.quit() # Quit if anything goes wrong
        return clips

def write_clips_to_db(clips):
    db = Mydb()
    for c in clips:
        db.add(c)
    db.commit()

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("cluster", nargs='+', help="clusterfile with name(s) of twitch channel (creator)")
    parser.add_argument("--wait", default='7', help="time in seconds to wait for page to load clip cards")
    parser.add_argument("--creators", action="store_true", help="set if list of creators")
    parser.add_argument("--interval", default="30d", help="pick one of 24hr,7d,30d,all")
    return parser.parse_args()

def get_list_creators(args) -> list:
    # returns list of Creator
    if args.creators:
        creators = list(map(Creator, args.cluster))
    else:
        creators = []
        for c in args.cluster:
            creators += CLUSTERS.by_name(c).creators
    return creators

def find_creator_interval_urls(args):
    creators = get_list_creators(args)
    twitch_clip_page_driver = TwitchClipPageSeleniumDriver()
    for creator in creators:
        print(creator.name)
        clips = twitch_clip_page_driver.find_creator_clips(creator, args)
        print(f"Found: {len(clips)} clips!")
        write_clips_to_db(clips)
    twitch_clip_page_driver.driver.quit()

if __name__ == "__main__":
    args = argparser()
    find_creator_interval_urls(args)