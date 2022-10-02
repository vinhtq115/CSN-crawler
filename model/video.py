from pathlib import Path
from typing import Union

import requests
from bs4 import BeautifulSoup

from model.exceptions import *
from model.logger import logging
from model.utils import is_error, download, extract_id


DOWNLOAD_QUALITIES = {
    0: ('flac', '.mp4'),  # 1080p
    1: ('m4a', '.mp4'),  # 720p
    2: ('320', '.mp4'),  # 480p
    3: ('128', '.mp4'),  # 360p
    4: ('32', '.mp4')  # 180p
}


class Video:
    def __init__(
        self,
        video_id: str
    ):
        """Initialize Video.

        Args:
            video_id (str): Video id. 

        Raises:
            NetworkError: If site cannot be reached
            NotFoundError: If site returns 404
            Error: Unknown errors
        """
        self.video_id = video_id
        
        # Parse page
        try:
            page = requests.get(f'https://chiasenhac.vn/hd/{self.video_id}.html')
        except NetworkError as e:
            logging.error(f'Failed to get info of video {self.video_id}.')
            raise e

        soup = BeautifulSoup(page.text, 'html.parser')
        wrapper = soup.findChildren(class_='wrapper_content')[0]
        container = wrapper.findChildren(class_='container', recursive=False)[0]
        
        # Check for error
        error_code = is_error(container)
        if error_code == '404':
            raise NotFoundError(f'Video id {self.video_id} not found.')
        elif error_code != False:
            raise Error(f'Unknown error. Code: {error_code}')
        
        # Get info
        logging.info(f'Getting info of track {self.video_id}.')
        card_body = container.findAll(class_='card-body')[0]

        # Get video title
        self.video_title = card_body.findAll(class_='card-title')[0].text

        # Get artists, composers, album and year info
        info_list = card_body.find('ul')
        self.artists = []
        self.artist_ids = []
        self.composers = None
        self.published_year = None
        
        for item in info_list.findAll('li'):
            text = item.text
            if text[:text.find(':')] == 'Ca sĩ':
                artists = item.findAll('a')
                for artist in artists:
                    self.artists.append(artist.text)
                    self.artist_ids.append(extract_id(artist['href']))
            elif text[:text.find(':')] == 'Sáng tác':
                self.composers = text[text.find(':') + 2:]
            elif text[:text.find(':')] == 'Năm phát hành':
                self.published_year = int(text[text.rfind(' ') + 1:])

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
        quality_id: int = 0,
    ):
        """Download video to specified directory. If chosen quality is not available,
        automatically downgrade to highest one available.

        Args:
            save_dir (Union[str, Path]): Destination directory
            quality_id (int, optional): Quality ID. 0 = 10880p, 1 = 720p, 2 = 480p, 3 = 360p, 4 = 180p. Defaults to 0.
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
        resp = requests.head(download_link)
        while resp.status_code in [404, 302] and quality_id < 4:
            # If specified quality is not available for current track, try lower quality
            logging.warning(f'Download link for quality "{quality}" of video {self.video_id} returned 404 error. Trying lower quality.')
            quality_id += 1
            quality, extension = DOWNLOAD_QUALITIES[quality_id]
            download_link = f'{self.base_download_path}/{quality}/{self.filename}{extension}'
            resp = requests.head(download_link)
        
        if resp.status_code in [404, 302]:
            raise NotFoundError(f'Cannot find available download link for {self.video_id}.')
        elif resp.status_code >= 400:
            raise Error(f'Unknown error.')

        # Download
        logging.info(f'Downloading video {self.video_id} with quality {quality}.')
        filename = f'{self.artists_name} - {self.video_title} [{self.video_id}]{extension}'
        download_path = Path(save_dir) / filename
        download(download_link, download_path)
        logging.info(f'Downloaded video {self.video_id} to {str(download_path.absolute())}.')

        return download_path
