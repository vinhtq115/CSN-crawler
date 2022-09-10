from pathlib import Path
from typing import Union

import requests
from bs4 import BeautifulSoup

from model.exceptions import *
from model.logger import logging
from model.utils import is_error


DOWNLOAD_QUALITIES = {
    0: ('flac', '.flac'),  # FLAC
    1: ('m4a', '.m4a'),  # M4A 500kbps
    2: ('320', '.mp3'),  # MP3 320kbps
    3: ('128', '.mp3'),  # MP3 128kbps
    4: ('32', '.m4a')  # M4A 32kbps
}


class Track:
    def __init__(
        self,
        track_id: str
    ):
        """Initialize Track.

        Args:
            track_id (str): Track id. 

        Raises:
            NetworkError: If site cannot be reached
            NotFoundError: If site returns 404
            Error: Unknown errors
        """
        self.track_id = track_id
        
        # Parse page
        try:
            page = requests.get(f'https://chiasenhac.vn/mp3/{self.track_id}.html')
        except requests.exceptions.RequestException as e:
            logging.error(e)
            raise NetworkError

        soup = BeautifulSoup(page.text, 'html.parser')
        wrapper = soup.findChildren(class_='wrapper_content')[0]
        container = wrapper.findChildren(class_='container', recursive=False)[0]
        
        # Check for error
        error_code = is_error(container)
        if error_code == '404':
            raise NotFoundError(f'Song id {self.track_id} not found.')
        elif error_code != False:
            raise Error(f'Unknown error. Code: {error_code}')
        
        # Get info
        logging.info(f'Getting info of track {self.track_id}.')
        card_body = container.findAll(class_='card-body')[0]

        # Get song title
        self.song_title = card_body.findAll(class_='card-title')[0].text

        # Get artists, composers, album and year info
        info_list = card_body.find('ul')
        self.artists = []
        self.artist_ids = []
        self.composers = None
        self.album = None
        self.album_id = None
        self.published_year = None
        
        for item in info_list.findAll('li'):
            text = item.text
            if text[:text.find(':')] == 'Ca sĩ':
                artists = item.findAll('a')
                for artist in artists:
                    self.artists.append(artist.text)
                    a_id = artist['href']
                    a_id = a_id.split('/')[-1]
                    self.artist_ids.append(a_id[a_id.rfind('-') + 1 : a_id.rfind('.')])
            elif text[:text.find(':')] == 'Sáng tác':
                self.composers = text[text.find(':') + 2:]
            elif text[:text.find(':')] == 'Năm phát hành':
                self.published_year = int(text[text.rfind(' ') + 1:])
            elif text[:text.find(':')] == 'Album':
                self.album = text[text.find(':') + 2:]
                b_id = item.findAll('a')[0]['href']
                b_id = b_id.split('/')[-1]
                self.album_id = b_id[b_id.rfind('-') + 1 : b_id.rfind('.')]

        # Get download link
        download_items = soup.findChildren(class_='download_item')
        _download_link = download_items[0]['href']
        # Filename
        filename = _download_link.split('/')[-1]
        self.filename = filename[:filename.rfind('.')]
        # Base download path
        base_download_path = _download_link[:_download_link.rfind('/')]
        self.base_download_path = base_download_path[:base_download_path.rfind('/')]

    @property
    def artists_name(self):
        if len(self.artists) == 1:
            return self.artists[0]
        elif len(self.artists) == 2:
            return f'{self.artists[0]} & {self.artists[1]}'
        else:
            _first = ', '.join(self.artists[:-1])
            return f'{_first} & {self.artists[-1]}'

    def download(
        self,
        save_dir: Union[str, Path],
        quality_id: int = 0
    ):
        """Download track to specified directory. If chosen quality is not available,
        automatically downgrade to highest one available.

        Args:
            save_dir (Union[str, Path]): Destination directory
            quality_id (int, optional): Quality ID. 0 = Lossless FLAC, 1 = M4A 500kbps, 2 = MP3 320kbps, 3 = MP3 128kbps, 4 = M4A 32kbps. Defaults to 0.

        Raises:
            InvalidQualityError: `quality_id` not in range [0, 4]
            NotFoundError: No download links available
            Error: Unknown error
        """
        # Check if chosen quality is valid
        if int(quality_id) > 4 or int(quality_id) < 0:
            raise InvalidQualityError(quality_id)

        # Create directory
        Path.mkdir(Path(save_dir).parent, exist_ok=True)

        # Try download with specified quality.
        quality, extension = DOWNLOAD_QUALITIES[quality_id]
        download_link = f'{self.base_download_path}/{quality}/{self.filename}{extension}'
        resp = requests.get(download_link)
        while resp.status_code == 404 and quality_id < 4:
            # If specified quality is not available for current track, try lower quality
            logging.warning(f'Download link for quality "{quality}" of track {self.track_id} returned 404 error. Trying lower quality.')
            quality_id += 1
            quality, extension = DOWNLOAD_QUALITIES[quality_id]
            download_link = f'{self.base_download_path}/{quality}/{self.filename}{extension}'
            resp = requests.get(download_link)
        
        if resp.status_code == 404:
            raise NotFoundError(f'Cannot find available download link for {self.track_id}.')
        elif resp.status_code >= 400:
            raise Error(f'Unknown error.')

        # Download
        logging.info(f'Downloading track {self.track_id} with quality {quality}.')
        filename = f'{self.artists_name} - {self.song_title} [{self.track_id}]{extension}'
        download_path = Path(save_dir) / filename
        with open(download_path, 'wb') as f:
            f.write(resp.content)
        logging.info(f'Downloaded track {self.track_id} to {str(download_path.absolute())}.')

        return True
