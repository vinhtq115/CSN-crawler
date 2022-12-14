from pathlib import Path
from typing import Union
import time

import requests

from bs4.element import Tag
from tqdm import tqdm

from model.exceptions import *

def is_error(container: Tag):
    # Check for error
    error_containers = container.findChildren(class_='error-container')
    if len(error_containers) > 0:
        error_code = error_containers[0].findChildren(class_='text-danger')[-1].text
        return error_code
    return False


def download(url: str, dest: Union[Path, str]):
    filename = Path(dest).name
    size = int(requests.head(url).headers['Content-Length'])

    with requests.get(url, stream=True) as src, \
            open(dest, 'wb') as f, \
            tqdm(unit='B', unit_scale=True, unit_divisor=1024, total=size, desc=filename) as progress:
        for chunk in src.iter_content(chunk_size=4096):
            progress.update(f.write(chunk))


def extract_id(url: str):
    res = url.split('/')[-1]
    res = res[res.rfind('-') + 1 : res.rfind('.')]
    return res

def get(url: str, retry: int = 5) -> requests.Response:
    consecutive_count = 0
    while True:
        try:
            page = requests.get(url)
            break
        except Exception as e:
            time.sleep(1)
            consecutive_count += 1
            if consecutive_count > retry:
                raise NetworkError
    return page
