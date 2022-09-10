import re

import requests
from bs4 import BeautifulSoup

from model.exceptions import *
from model.logger import logging
from model.utils import is_error


artist_id_pattern = re.compile('\'artist_id\': \'[0-9]+\'')


class Artist:
    def __init__(
        self,
        artist_id: str
    ):
        self.artist_id = artist_id

        # Parse page
        try:
            page = requests.get(f'https://chiasenhac.vn/ca-si/{self.artist_id}.html')
        except requests.exceptions.RequestException as e:
            logging.error(e)
            raise NetworkError

        soup = BeautifulSoup(page.text, 'html.parser')
        wrapper = soup.findChildren(class_='wrapper_content')[0]
        container = wrapper.findChildren(class_='container', recursive=False)[0]

        # Check for error
        error_code = is_error(container)
        if error_code == '404':
            raise NotFoundError(f'Artist id {self.artist_id} not found.')
        elif error_code != False:
            raise Error(f'Unknown error. Code: {error_code}')
        
        # Get info
        self.artist_name = wrapper.findChild(class_='artist_name_box').text
        self.artist_id_number = int(re.findall('\d+', artist_id_pattern.findall(page.text)[0])[0])

        logging.info(f'Getting song list of artist {self.artist_name} [{self.artist_id_number}] [{self.artist_id}].')
        number_of_pages = int(container.findChild(id='music').find('center').text.split(' ')[-1])
        
        self.songs = self.get_all_songs(number_of_pages)

    def get_all_songs(self, number_of_pages: int) -> set:
        """Get all songs of an artist.

        Args:
            number_of_pages (int): Number of pages (from artist page).

        Returns:
            set: Song IDs.
        """
        song_ids = set()

        for page_idx in range(number_of_pages):
            logging.info(f'Parsing page {page_idx + 1}/{number_of_pages} of music tab of artist {self.artist_name} [{self.artist_id_number}].')
            url = f'https://chiasenhac.vn/tab_artist?page={page_idx + 1}&artist_id={self.artist_id_number}&tab=music'
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')

            songs = soup.findAll(class_='media')
            for song in songs:
                # Get song id
                href = song.findChildren(class_='media-title')[0].find('a')['href']
                s_id = href.split('/')[-1]
                s_id = s_id[s_id.rfind('-') + 1 : s_id.rfind('.')]
                song_ids.add(s_id)

        return song_ids