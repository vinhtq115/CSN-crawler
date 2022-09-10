from pathlib import Path
from typing import Union

import requests
from bs4 import BeautifulSoup

from model.exceptions import *
from model.logger import logging


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
        self.track_id = track_id
        
        # Parse page
        self.url = f'https://chiasenhac.vn/mp3/{self.track_id}.html'
        try:
            page = requests.get(self.url)
        except requests.exceptions.RequestException as e:
            logging.error(e)
            raise NetworkError

        self.soup = BeautifulSoup(page.text, 'html.parser')
        wrapper = self.soup.findChildren(class_='wrapper_content')[0]
        self.container = wrapper.findChildren(class_='container', recursive=False)[0]
        
        # Check for error
        error_containers = self.container.findChildren(class_='error-container')
        if len(error_containers) > 0:
            error_code = error_containers[0].findChildren(class_='text-danger')[-1].text
            if error_code == '404':
                raise NotFoundError(f'Song id {self.track_id} not found.')
            else:
                raise Error(f'Unknown error. Code: {error_code}')
        
        # Get info
        logging.info(f'Getting info of track {self.track_id}.')
        self.get_info()
        
    def get_info(self):
        card_body = self.container.findAll(class_='card-body')[0]

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
        # Check if chosen quality is valid
        if int(quality_id) > 4 or int(quality_id) < 0:
            raise InvalidQualityError(quality_id)

        # Create directory
        Path.mkdir(Path(save_dir).parent, exist_ok=True)

        # Get download link
        download_items = self.soup.findChildren(class_='download_item')
        _download_link = download_items[0]['href']
        # Filename
        filename = _download_link.split('/')[-1]
        filename = filename[:filename.rfind('.')]
        # Base download path
        base_download_path = _download_link[:_download_link.rfind('/')]
        base_download_path = base_download_path[:base_download_path.rfind('/')]
        
        # Try download with specified quality.
        quality, extension = DOWNLOAD_QUALITIES[quality_id]
        download_link = f'{base_download_path}/{quality}/{filename}{extension}'
        resp = requests.get(download_link)
        while resp.status_code == 404 and quality_id < 4:
            # If specified quality is not available for current track, try lower quality
            logging.warning(f'Download link for quality "{quality}" of track {self.track_id} returned 404 error. Trying lower quality.')
            quality_id += 1
            quality, extension = DOWNLOAD_QUALITIES[quality_id]
            download_link = f'{base_download_path}/{quality}/{filename}{extension}'
            resp = requests.get(download_link)
        
        if resp.status_code == 404:
            raise Error(f'Cannot find available download link for {self.track_id}.')
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

if __name__ == '__main__':
    track = Track('ts3w7z5wq9t1h9')
    track.download('/Users/vinhtq115/.tmpdisk/ramdisk', 0)
