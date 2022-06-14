#!/usr/bin/python3
from model.cluster import Creator


class Clip:
    def __init__(
        self,
        creator: Creator,
        request: dict,
        game: str,
        ):
        self.creator: Creator = creator
        #self.broadcaster_id = request['broadcaster_id']
        #self.creator_id  = request['creator_id']
        #self.embed_url = request['embed_url']
        #self.video_id  = request['video_id']
        #self.broadcaster_name: str = request['broadcaster_name']
        self.created_at: str = self._created_at(request['created_at'])
        self.clipper_name: str = request['creator_name']
        self.duration: float = request['duration']
        self.game_id: str = request['game_id']
        self.game: str = game
        self.language: str = self._language(request['language'])
        self.thumbnail_url: str = request['thumbnail_url']
        self.title: str = request['title']
        self.url: str = request['url']
        self.view_count: int = request['view_count']

    def _created_at(self, x: str) -> str:
        return x.split('T')[0]

    def _language(self, x: str) -> str:
        return x if x!='en-gb' else 'en'
