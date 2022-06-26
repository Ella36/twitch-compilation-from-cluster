#!/usr/bin/python3
import sqlite3
import pandas as pd

from .clips import Clip


class Mydb():
    def __init__(self):
        self.con = sqlite3.connect('file:clips.db')
        self.cur = self.con.cursor()

    def close(self):
        self.con.close()

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

    def read_clips_clip_ids_df_from_db(self, urls: list) -> pd.DataFrame:
        urls_str = '('+','.join([f"'{u}'" for u in urls])+')'
        df = pd.read_sql_query(
            f"SELECT * FROM clips WHERE url IN {urls_str}",
            self.con
        )
        return df

    def read_clips_creators_df_from_db(self, creators: list) -> pd.DataFrame:
        creators_str = '('+','.join([f"'{c.lower()}'" for c in creators])+')'
        df = pd.read_sql_query(
            f"SELECT * FROM clips WHERE creator IN {creators_str}",
            self.con
        )
        return df

    def read_clips_categories_df_from_db(self, categories: list) -> pd.DataFrame:
        creators_str = '('+','.join([f"'{c}'" for c in categories])+')'
        df = pd.read_sql_query(
            f"SELECT * FROM clips WHERE game IN {creators_str}",
            self.con
        )
        return df

    def read_clips_categories_by_id_df_from_db(self, game_ids: list) -> pd.DataFrame:
        game_id_str = '('+','.join([f"'{c}'" for c in game_ids])+')'
        df = pd.read_sql_query(
            f"SELECT * FROM clips WHERE game_id IN {game_id_str}",
            self.con
        )
        return df

    def read_compilations_df_from_db(self) -> pd.DataFrame:
        # id, creators, urls, duration, time, project
        df = pd.read_sql_query(
            "SELECT * FROM compilations",
            self.con
        )
        return df


    def set_publish_temp(self, url: str):
        self.cur.execute(f"UPDATE clips SET published = '1' where url = '{url}'")

    def set_published_from_compilations(self):
        def _set_publish(self, url: str):
            self.cur.execute(f"UPDATE clips SET published = '1' where url = '{url}'")
        def _set_all_clips_unpublished(self):
            self.cur.execute(f"UPDATE clips SET published = '0'")
        _set_all_clips_unpublished(self)
        df = self.read_compilations_df_from_db()
        urls = []
        for _, row in df.iterrows():
            # creator_names = row["creators"].split(',')
            urls += row["urls"].split(',')
            # duration = row["duration"]
            # time = row["time"]
        for url in urls:
            _set_publish(self, url)
        self.con.commit()
        print('Set published flags in clips table from compilations table!')
    
    def create_compilation(self):
        self.cur.execute('''DROP table IF EXISTS compilations''')
        self.cur.execute('''CREATE TABLE compilations
                    (id integer primary key autoincrement, creators text, urls text, duration integer, time text, project text, integer pid) ''')
        self.con.commit()
        print('Created table compilations!')

    def add_compilation(self, creators: str, urls: str, duration: int, time: str, project: str, pid: int):
        self.cur.execute('INSERT INTO compilations(creators, urls, duration, time, project, pid) VALUES (?,?,?,?,?,?)', (creators, urls, duration, time, project, pid))

    def select_latest_compilation_number(self, project: str) -> int:
        # Project is like projectname_interval  
        #self.cur.execute("""SELECT pid FROM compilations WHERE project=? ORDER BY id DESC LIMIT 1""", (project,))
        self.cur.execute(f"""SELECT COUNT(pid) FROM compilations WHERE project LIKE '{project.split('_')[0]}_%'""")
        return self.cur.fetchone()

    def select_thumbnail_url(self, url: str) -> str:
        self.cur.execute("""SELECT thumbnail_url FROM clips WHERE url=?""", (url,))
        return self.cur.fetchone()[0]

    def lookup_url(self, url: str) -> dict:
        self.cur.execute("""SELECT * FROM clips WHERE url=?""", (url,))
        return self.cur.fetchone()

    def is_url_in(self, url: str) -> bool:
        self.cur.execute("""SELECT url FROM clips WHERE url=?""", (url,))
        return True if self.cur.fetchone() else False

    def set_broken(self, url: str):
        self.cur.execute(f"UPDATE clips SET broken = '1' where url = '{url}'")
    
    def add(self, clip: Clip):
        # Add unpublished clip
        published = 0
        broken = 0
        row  = self.lookup_url(clip.url)
        if row:
            broken = row[-1]
            published = row[-2]
            self.cur.execute("""DELETE FROM clips WHERE url=?""", (clip.url,))
        clip.title = clip.title.replace("'", "''")
        clip.game = clip.game.replace("'", "''")
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