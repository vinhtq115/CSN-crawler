import re

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from model.exceptions import *
from model.logger import logging
from model.track import Track
from model.utils import extract_id, is_error


artist_id_pattern = re.compile('\'artist_id\': \'[0-9]+\'')


class Album:
    def __init__(
        self,
        album_id: str
    ):
        """Initialize Album.

        Args:
            album_id (str): Album id.

        Raises:
            NetworkError: If site cannot be reached
            NotFoundError: If site returns 404
            Error: Unknown errors
        """
        self.album_id = album_id

        # Parse page
        try:
            page = requests.get(f'https://chiasenhac.vn/nghe-album/{self.album_id}.html')
        except requests.exceptions.RequestException as e:
            logging.error(e)
            raise NetworkError

        soup = BeautifulSoup(page.text, 'html.parser')
        wrapper = soup.findChildren(class_='wrapper_content')[0]
        container = wrapper.findChildren(class_='container', recursive=False)[0]

        # Check for error
        error_code = is_error(container)
        if error_code == '404':
            raise NotFoundError(f'Album id {self.artist_id} not found.')
        elif error_code != False:
            raise Error(f'Unknown error. Code: {error_code}')
        
        # Get info
        logging.info(f'Getting info of album {self.album_id}.')
        card_body = container.findChildren(class_='card-details')[0].findChildren(class_='card-body')[0]
        card_body = card_body.findAll('li')

        self.album_name = None
        self.year_published = None

        for item in card_body:
            if item.text.startswith('Album: '):
                self.album_name = item.text[item.text.find(':') + 2:]
            elif item.text.startswith('Năm phát hành: '):
                self.year_published = int(item.text[item.text.find(':') + 2:])
        
        # Get track list
        logging.info(f'Getting tracklist of album {self.album_name} [{self.album_id}].')
        song_table = container.find(class_='d-table')
        self.tracklist = self.get_tracklist(song_table)

    def get_tracklist(self, song_table: Tag) -> list[dict]:
        """Get tracklist of album

        Args:
            song_table (Tag): Song table from page

        Returns:
            list[dict]: List of songs
        """
        song_list = []

        for tag in song_table:
            if not isinstance(tag, Tag):
                continue
            
            if tag.attrs.get('id') is None or not tag.attrs['id'].startswith('music-listen'):
                continue
            
            song_no = tag.find(class_='name').find('a').text
            song_no = int(song_no[:song_no.find('.')])
            song_title = tag.find(class_='name').find('a')['title']
            song_id = extract_id(tag.find(class_='list-inline-item').find('a')['href'])
            song_list.append({
                'title': song_title,
                'number': song_no,
                'id': song_id
            })

        return song_list
