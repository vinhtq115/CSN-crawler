import re

from bs4 import BeautifulSoup

from model.exceptions import *
from model.logger import logging
from model.utils import extract_id, is_error, get


artist_id_pattern = re.compile('\'artist_id\': \'[0-9]+\'')
NO_SONGS = re.compile('Chưa có bài hát nào')
NO_ALBUMS = re.compile('Chưa có album nào')
NO_VIDEOS = re.compile('Chưa có video nào')

class Artist:
    def __init__(
        self,
        artist_id: str = None,
        artist_id_number: int = None
    ):
        """Initialize Artist. Must be initialized with artist_id or artist_id_number.

        Args:
            artist_id (str): Artist id.
            artist_id_number (int): Artist id number.

        Raises:
            AssertionError:
            NetworkError: If site cannot be reached
            NotFoundError: If site returns 404
            Error: Unknown errors
        """
        if artist_id is None and artist_id_number is None:
            raise AssertionError('Both artist_id and artist_id_number must not be empty')

        if artist_id is not None:
            a_id = artist_id
        elif artist_id_number is not None:
            a_id = artist_id_number

        # Parse page
        try:
            page = get(f'https://chiasenhac.vn/ca-si/{a_id}.html')
        except NetworkError as e:
            logging.error(f'Failed to get info of artist {a_id}.')
            raise e

        soup = BeautifulSoup(page.text, 'html.parser')
        wrapper = soup.findChildren(class_='wrapper_content')[0]
        container = wrapper.findChildren(class_='container', recursive=False)[0]

        # Check for error
        error_code = is_error(container)
        if error_code == '404':
            raise NotFoundError(f'Artist id {a_id} not found.')
        elif error_code != False:
            raise Error(f'Unknown error. Code: {error_code}')
        
        # Get info
        self.artist_id = page.url.split('/')[-1]
        self.artist_id = self.artist_id[self.artist_id.rfind('-') + 1:self.artist_id.rfind('.html')]
        self.artist_name = wrapper.findChild(class_='artist_name_box').text
        self.artist_id_number = int(re.findall('\\d+', artist_id_pattern.findall(page.text)[0])[0])

    def get_all_songs(self) -> set:
        """Get all songs of an artist.

        Returns:
            set: Song IDs.
        """
        song_ids = set()

        logging.info(f'Getting song list of artist {self.artist_name} [{self.artist_id_number}] [{self.artist_id}].')
        # Get total number of music pages
        url = f'https://chiasenhac.vn/tab_artist?artist_id={self.artist_id_number}&tab=music'
        try:
            page = get(url)
        except NetworkError as e:
            logging.error(f'Failed to get songs of artist {self.artist_id}.')
            raise e

        if NO_SONGS.search(page.text):
            return song_ids
        
        soup = BeautifulSoup(page.text, 'html.parser')
        pagination = soup.findAll(class_='pagination')[0]
        number_of_pages = int(pagination.findAll('li')[-1].text)

        for page_idx in range(number_of_pages):
            logging.info(f'Parsing page {page_idx + 1}/{number_of_pages} of music tab of artist {self.artist_name} [{self.artist_id_number}].')
            url = f'https://chiasenhac.vn/tab_artist?page={page_idx + 1}&artist_id={self.artist_id_number}&tab=music'
            try:
                page = get(url)
            except NetworkError as e:
                logging.error(f'Failed to get songs on page {page_idx + 1} of artist {self.artist_id}.')
                raise e
            soup = BeautifulSoup(page.text, 'html.parser')

            songs = soup.findAll(class_='media')
            for song in songs:
                # Get song id
                href = song.findChildren(class_='media-title')[0].find('a')['href']
                song_ids.add(extract_id(href))

        return song_ids
    
    def get_all_videos(self) -> set:
        """Get all videos of an artist.

        Returns:
            set: Video IDs.
        """
        videos_ids = set()

        logging.info(f'Getting video list of artist {self.artist_name} [{self.artist_id_number}] [{self.artist_id}].')
        # Get total number of video pages
        url = f'https://chiasenhac.vn/tab_artist?artist_id={self.artist_id_number}&tab=video'
        try:
            page = get(url)
        except NetworkError as e:
            logging.error(f'Failed to get videos of artist {self.artist_id}.')
            raise e

        if NO_VIDEOS.search(page.text):
            return videos_ids
        
        soup = BeautifulSoup(page.text, 'html.parser')
        pagination = soup.findAll(class_='pagination')[0]
        number_of_pages = int(pagination.findAll('li')[-1].text)

        for page_idx in range(number_of_pages):
            logging.info(f'Parsing page {page_idx + 1}/{number_of_pages} of video tab of artist {self.artist_name} [{self.artist_id_number}].')
            url = f'https://chiasenhac.vn/tab_artist?page={page_idx + 1}&artist_id={self.artist_id_number}&tab=video'
            try:
                page = get(url)
            except NetworkError as e:
                logging.error(f'Failed to get videos on page {page_idx + 1} of artist {self.artist_id}.')
                raise e
            soup = BeautifulSoup(page.text, 'html.parser')

            videos = soup.findAll(class_='card-title')
            for video in videos:
                # Get video id
                href = video.find('a')['href']
                videos_ids.add(extract_id(href))

        return videos_ids

    def get_all_albums(self) -> set:
        """Get all albums of an artist.

        Returns:
            set: Album IDs.
        """
        albums_ids = set()

        logging.info(f'Getting album list of artist {self.artist_name} [{self.artist_id_number}] [{self.artist_id}].')
        # Get total number of album pages
        url = f'https://chiasenhac.vn/tab_artist?artist_id={self.artist_id_number}&tab=album'
        try:
            page = get(url)
        except NetworkError as e:
            logging.error(f'Failed to get albums of artist {self.artist_id}.')
            raise e

        if NO_ALBUMS.search(page.text):
            return albums_ids

        soup = BeautifulSoup(page.text, 'html.parser')
        pagination = soup.findAll(class_='pagination')[0]
        number_of_pages = int(pagination.findAll('li')[-1].text)

        for page_idx in range(number_of_pages):
            logging.info(f'Parsing page {page_idx + 1}/{number_of_pages} of album tab of artist {self.artist_name} [{self.artist_id_number}].')
            url = f'https://chiasenhac.vn/tab_artist?page={page_idx + 1}&artist_id={self.artist_id_number}&tab=album'
            try:
                page = get(url)
            except NetworkError as e:
                logging.error(f'Failed to get albums on page {page_idx + 1} of artist {self.artist_id}.')
                raise e
            soup = BeautifulSoup(page.text, 'html.parser')

            albums = soup.findAll(class_='card-title')
            for album in albums:
                # Get album id
                href = album.find('a')['href']
                albums_ids.add(extract_id(href))

        return albums_ids