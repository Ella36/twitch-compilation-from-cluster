#!/usr/bin/python3
import sqlite3


class Mydb():
    def __init__(self):
        self.con = sqlite3.connect('file:clips.db')
        self.cur = self.con.cursor()

    def create_clips(self):
        self.cur.execute('''DROP table IF EXISTS clips''')
        self.cur.execute('''CREATE TABLE clips
            (creator text, url text primary key, duration float,
            view_count integer, created_at text, game text,
            clipper_name text, game_id text, language text, 
            thumbnail_url text, title text,
            published integer, broken integer) ''')
        self.con.commit()
        print('Created table clips!')

    def create_script(self):
        self.cur.execute('''DROP table IF EXISTS scripts''')
        self.cur.execute('''CREATE TABLE scripts
                    (id integer primary key autoincrement, creators text, urls text, duration integer, time text) ''')
        self.con.commit()
        print('Created table scripts!')

    def add_script(self, creators: str, urls: str, duration: int, time: str):
        self.cur.execute('INSERT INTO scripts(creators, urls, duration, time) VALUES (?,?,?,?)', (creators, urls, duration, time))

    def select_latest_script_number(self) -> int:
        self.cur.execute("""SELECT id FROM scripts ORDER BY id DESC LIMIT 1""")
        return int(self.cur.fetchone()[0])

    def lookup_url(self, url: str) -> dict:
        self.cur.execute("""SELECT * FROM clips WHERE url=?""", (url,))
        return self.cur.fetchone()

    def is_url_in(self, url: str) -> bool:
        self.cur.execute("""SELECT url FROM clips WHERE url=?""", (url,))
        return True if self.cur.fetchone() else False

    def set_publish(self, url: str):
        self.cur.execute(f"UPDATE clips SET published = '1' where url = '{url}'")

    def set_broken(self, url: str):
        self.cur.execute(f"UPDATE clips SET broken = '1' where url = '{url}'")
    
    def add(self, clip):
        # Add unpublished clip
        published = 0
        broken = 0
        if self.is_url_in(clip.url):
            print(f'Duplicate not added:\n\t{clip.url}\n\t{clip.title}')
            return
        clip.title = clip.title.replace("'", "''")
        string = (
            f"INSERT INTO clips VALUES ('{clip.creator.name}','{clip.url}','{clip.duration}',"
            f"'{clip.view_count}','{clip.created_at}','{clip.game}',"
            f"'{clip.clipper_name}','{clip.game_id}','{clip.language}',"
            f"'{clip.thumbnail_url}','{clip.title}',"
            f"'{published}','{broken}')"
                 )
        self.cur.execute(string)
    
    def commit(self):
        self.con.commit()

import argparse
def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--scripts', action='store_true', help='create table scripts')
    parser.add_argument('-c', '--clips', action='store_true', help='create table clips')
    return parser.parse_args()

if __name__ == '__main__':
    args = argparser()
    db = Mydb()
    if args.scripts:
        db.create_script()
    if args.clips:
        db.create_clips()