#!/usr/bin/python3
import argparse
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from datetime import timedelta, datetime

from model.cluster import CLUSTERS
from model.cluster import Creator
from model.clip import Clip
from db.mydb import Mydb


twitch_credentials = {
   "client_id": "3v7w9gbeuaz6d6hiwlk448nw7lrsl3",
   "client_secret": "n23yzkko4ewa4oguwx962pkbg55uby"
}

# category, language="en"

from model import twitch_api

class TwitchSelectorRequests():
    def __init__(self):
        self.twitch_oauth_header = twitch_api.login(twitch_credentials)

    def get_clips_from_category(self, category_name: str, args):
        started_at=datetime.utcnow() - timedelta(days=int(args.days))
        ended_at=datetime.utcnow() - timedelta(hours=12)
        requests = twitch_api.get_clips_request_by_category(
            self.twitch_oauth_header, category_name, started_at, ended_at
        )
        def _format_to_clip(request: dict) -> Clip:
            return Clip(Creator(request['broadcaster_name']), request, category_name)
        clips_formatted = list(map(_format_to_clip, requests))
        return clips_formatted

    def get_clips_from_creator(self, creator: Creator, args):
        started_at=datetime.utcnow() - timedelta(days=int(args.days))
        ended_at=datetime.utcnow() - timedelta(hours=12)
        requests = twitch_api.get_clips_request_by_streamer(
            self.twitch_oauth_header, creator.name, started_at, ended_at
        )
        def _format_to_clip(request: dict) -> Clip:
            try:
                game = twitch_api.TWITCH_GAME_ID_TO_NAME.id_to_game(request['game_id'])
            except IndexError:
                game = "unknown"
                print(f"Game not found!\n\t{request['url']}\n\t{request['title']}")
            return Clip(creator, request, game)
        clips_formatted = list(map(_format_to_clip, requests))
        return clips_formatted


def write_clips_to_db(clips):
    db = Mydb()
    for c in clips:
        db.add(c)
    db.commit()

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("cluster", nargs='+', help="clusterfile with name(s) of twitch channel (creator)")
    parser.add_argument("--creators", action="store_true", help="set if list of creators")
    parser.add_argument("--category", action="store_true", help="set if input is category ex 'Just Chatting'")
    parser.add_argument("--days", default="30", help="pick n days")
    return parser.parse_args()

def get_list_creators(args) -> list:
    if args.creators:
        creators = list(map(Creator, args.cluster))
    else:
        creators = []
        for c in args.cluster:
            creators += CLUSTERS.by_name(c).creators
    return creators

def find_creator_interval_urls(args):
    if args.category:
        twitch_clip_requests = TwitchSelectorRequests()
        for category in args.cluster:
            if not twitch_api.TWITCH_GAME_ID_TO_NAME.is_valid_game(category):
                print(f'Not valid category Check CAPS:\n\t{category}')
            print(category)
            clips = twitch_clip_requests.get_clips_from_category(category, args)
            print(f"Found: {len(clips)} clips!")
            write_clips_to_db(clips)
    else:
        creators = get_list_creators(args)
        twitch_clip_requests = TwitchSelectorRequests()
        for creator in creators:
            print(creator.name)
            clips = twitch_clip_requests.get_clips_from_creator(creator, args)
            print(f"Found: {len(clips)} clips!")
            write_clips_to_db(clips)


if __name__ == "__main__":
    args = argparser()
    find_creator_interval_urls(args)