from queue import Queue
from threading import Thread

import apsw

from model.logger import logging

class Database(Thread):
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self.queue = Queue()

        self.cursor = None
        self.start()

    def check_if_table_exists(self, table_name: str) -> bool:
        """Return True if table with specified name exists, else False.

        Args:
            table_name (str): name of table

        Returns:
            bool: True if table exists in database, else False
        """
        return self.cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=(?)", (table_name,)).fetchone()[0] == 1

    def has_required_tables(self) -> bool:
        """Check if database has all required tables

        Returns:
            bool: True if database has all required tables, else False.
        """
        return self.check_if_table_exists('artists') and \
            self.check_if_table_exists('albums') and \
            self.check_if_table_exists('tracks') and \
            self.check_if_table_exists('videos') and \
            self.check_if_table_exists('album_tracks') and \
            self.check_if_table_exists('artists_tracks') and \
            self.check_if_table_exists('artists_videos')

    def check_and_init_db(self):
        if self.has_required_tables():
            logging.info('Database has all required table.')
            return

        # Create table artists
        if not self.check_if_table_exists('artists'):
            logging.info('Creating table `artists`')
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS artists (
                    id text PRIMARY KEY,
                    name text,
                    id_number integer UNIQUE
                );
            """)

        # Create table albums
        if not self.check_if_table_exists('albums'):
            logging.info('Creating table `albums`')
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS albums (
                    id text PRIMARY KEY,
                    name text,
                    year_published integer
                );
            """)
        
        # Create table tracks
        if not self.check_if_table_exists('tracks'):
            logging.info('Creating table `tracks`')
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    id text PRIMARY KEY,
                    name text,
                    composer text,
                    album_id text DEFAULT NULL REFERENCES albums(id),
                    year_published integer,
                    download_path text DEFAULT NULL
                );
            """)

        # Create table videos
        if not self.check_if_table_exists('videos'):
            logging.info('Creating table `videos`')
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id text PRIMARY KEY,
                    name text,
                    composer text,
                    year_published integer,
                    download_path text DEFAULT NULL
                );
            """)

        # Create table album_tracks
        if not self.check_if_table_exists('album_tracks'):
            logging.info('Creating table `album_tracks`')
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS album_tracks (
                    album_id text,
                    track_id text,
                    track_idx integer,
                    FOREIGN KEY (album_id) REFERENCES albums(id),
                    FOREIGN KEY (track_id) REFERENCES tracks(id)
                );
            """)

        # Create table artists_tracks
        if not self.check_if_table_exists('artists_tracks'):
            logging.info('Creating table `artists_tracks`')
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS artists_tracks (
                    artists_id text,
                    track_id text,
                    FOREIGN KEY (artists_id) REFERENCES artists(id),
                    FOREIGN KEY (track_id) REFERENCES tracks(id)
                );
            """)

        # Create table artists_videos
        if not self.check_if_table_exists('artists_videos'):
            logging.info('Creating table `artists_videos`')
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS artists_videos (
                    artists_id text,
                    video_id text,
                    FOREIGN KEY (artists_id) REFERENCES artists(id),
                    FOREIGN KEY (video_id) REFERENCES videos(id)
                );
            """)

    def run(self):
        db = apsw.Connection(self.db_path)
        self.cursor = db.cursor()

        self.check_and_init_db()

        while True:
            req, args, res = self.queue.get()

            # Close if req is None
            if req is None:
                break

            self.cursor.execute(req, args)
            if res:
                for rec in self.cursor:
                    res.put(rec)
                res.put(None)

        db.close()
    
    def execute(self, request, args=None, res=None):
        self.queue.put((request, args or tuple(), res))
    
    def select(self, request, args=None):
        res = Queue()
        self.execute(request, args, res)
        while True:
            rec = res.get()
            if rec is None:
                break
            yield rec

    def close(self):
        self.execute(None)
