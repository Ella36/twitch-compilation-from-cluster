#!/usr/bin/env python
import requests
import pandas as pd

if __name__ == "__main__":
    from secrets import TWITCH_CREDENTIALS
else:
    from cfg.secrets import TWITCH_CREDENTIALS

TWITCH_OAUTH_ENDPOINT = "https://id.twitch.tv/oauth2/token"
TWITCH_CLIPS_ENDPOINT = "https://api.twitch.tv/helix/clips"
TWITCH_CATEGORY_ENDPOINT = "https://api.twitch.tv/helix/search/categories"
TWITCH_TOP_GAMES_ENDPOINT = "https://api.twitch.tv/helix/games/top"
TWITCH_BROADCASTER_ENDPOINT = "https://api.twitch.tv/helix/users"
TWITCH_GAMES_ENDPOINT = "https://api.twitch.tv/helix/games"


class TwitchGameIDtoName:
    def __init__(self):
        self.df = pd.read_csv('./model/game_info_semicolon.csv', sep=';')

    def is_valid_game(self, name: str):
        try:
           _ = self.df.loc[self.df['name'] == name].iloc[0]["id"]
           return True
        except IndexError:
            return False

    def id_to_game(self, idx: str):
        return self.df.loc[self.df['id'] == int(idx)]["name"].iloc[0]

    def game_to_id(self, name: str):
        return self.df.loc[self.df['name'] == name]["id"].iloc[0]

TWITCH_GAME_ID_TO_NAME = TwitchGameIDtoName()

def login(twitch_credentials):
    twitch_client_id = twitch_credentials["client_id"]
    twitch_client_secret = twitch_credentials["client_secret"]
    query_parameters = f'?client_id={twitch_client_id}&client_secret={twitch_client_secret}&grant_type=client_credentials'

    response = requests.post(TWITCH_OAUTH_ENDPOINT + query_parameters)
    if response.status_code != 200:
        raise Exception(f'An error occured while authenticating Twitch: {response.json()["message"]}')

    twitch_token = response.json()['access_token']
    twitch_oauth_header = {"Client-ID": twitch_client_id,
                           "Authorization": f"Bearer {twitch_token}"}

    return twitch_oauth_header


def get_request(twitch_oauth_header, endpoint_url, query_parameters, error_message="An error occurred"):
    response = requests.get(endpoint_url + query_parameters, headers=twitch_oauth_header)

    if response.status_code != 200:
        raise Exception(response.json())

    if response.json()["data"] is None:
        raise Exception(error_message)

    return response.json()["data"]


def get_top_categories(twitch_oauth_header, amount=20):
    categories_json = get_request(twitch_oauth_header, TWITCH_TOP_GAMES_ENDPOINT, f"?first={amount}")
    categories = []

    for category in categories_json:
        categories.append(category['name'])

    return categories


def get_category_id(twitch_credentials, category_name):
    query_parameters = f'?query={category_name}'
    error_message = f'Twitch category not found: "{category_name}"'
    category_list = get_request(twitch_credentials, TWITCH_CATEGORY_ENDPOINT, query_parameters, error_message)
    found_category = next((category for category in category_list if category["name"].lower() == category_name.lower()),
                          None)

    if found_category is None:
        raise Exception(f'Category with name "{category_name}" not found.')

    return found_category["id"]


def get_broadcaster_id(twitch_credentials, broadcaster_name):
    query_parameters = f'?login={broadcaster_name}'
    broadcaster_data = get_request(twitch_credentials, TWITCH_BROADCASTER_ENDPOINT, query_parameters)
    if len(broadcaster_data) == 0:
        raise Exception(f'Broadcaster with name "{broadcaster_name}" not found.')

    return broadcaster_data[0]["id"]


def get_clips_request_by_id(twitch_credentials, category_id, started_at, ended_at):
    started_at = started_at.isoformat("T") + "Z"
    ended_at = ended_at.isoformat("T") + "Z"
    query_parameters = f'?game_id={category_id}&first=100&started_at={started_at}&ended_at={ended_at}'
    return get_request(twitch_credentials, TWITCH_CLIPS_ENDPOINT, query_parameters)

def get_clips_request_by_clip_id(twitch_credentials, clip_id):
    query_parameters = f'?id={clip_id}'
    return get_request(twitch_credentials, TWITCH_CLIPS_ENDPOINT, query_parameters)

def get_clips_request_by_clip_url(twitch_credentials, clip_url):
    clip_id = clip_url.split('/')[-1]
    query_parameters = f'?id={clip_id}'
    return get_request(twitch_credentials, TWITCH_CLIPS_ENDPOINT, query_parameters)

def get_clips_request_by_category(twitch_credentials, category_name, started_at, ended_at):
    started_at = started_at.isoformat("T") + "Z"
    ended_at = ended_at.isoformat("T") + "Z"
    category_id = get_category_id(twitch_credentials, category_name)
    query_parameters = f'?game_id={category_id}&first=100&started_at={started_at}&ended_at={ended_at}'
    return get_request(twitch_credentials, TWITCH_CLIPS_ENDPOINT, query_parameters)


def get_clips_request_by_streamer(twitch_credentials, streamer_name, started_at, ended_at):
    started_at = started_at.isoformat("T") + "Z"
    ended_at = ended_at.isoformat("T") + "Z"
    broadcaster_id = get_broadcaster_id(twitch_credentials, streamer_name)
    query_parameters = f'?broadcaster_id={broadcaster_id}&first=100&started_at={started_at}&ended_at={ended_at}'
    return get_request(twitch_credentials, TWITCH_CLIPS_ENDPOINT, query_parameters)

def get_game_from_id(twitch_credentials, game_id):
    query_parameters = f'?id={game_id}'
    game_data = get_request(twitch_credentials, TWITCH_GAMES_ENDPOINT, query_parameters)
    if len(game_data) == 0:
        raise Exception(f'Game with id "{game_id}" not found.')
    return game_data[0]["name"]

if __name__ == "__main__":
    twitch_oauth_header = login(TWITCH_CREDENTIALS)

    game_names_tolookup = [
        "Disney Dreamlight Valley",
    ]

    game_ids_to_lookup = [
    ]

    for game_name in game_names_tolookup:
        try:
            game_id = get_category_id(twitch_oauth_header, game_name)
            with open('./model/game_info_semicolon.csv', "a") as f:
                print(f'\n"{game_id}";"{game_name}";""')
                f.write(f'\n"{game_id}";"{game_name}";""')
        except Exception:
            print(f"Not found {game_name}")
            pass

    for game_id in game_ids_to_lookup:
        try:
            game_name = get_game_from_id(twitch_oauth_header, game_id)
            with open('./model/game_info_semicolon.csv', "a") as f:
                print(f'\n"{game_id}";"{game_name}";""')
                f.write(f'\n"{game_id}";"{game_name}";""')
        except Exception:
            print(f"Not found {game_id}")
            pass
