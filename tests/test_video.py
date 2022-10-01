from tempfile import TemporaryDirectory
from pathlib import Path
import sys
sys.path.append('./')

import pytest
from model.exceptions import *

from model.video import Video


temp_dir = TemporaryDirectory()


def test_video1():
    video = Video('vs33smzvqw4812')
    assert video.video_title == 'Lặng Yêu'
    assert video.artists_name == 'Khánh Phương & Từ Minh Hy'
    assert 'zss7twqsqtf9e4' in video.artist_ids and 'zsswzmq7q918et' in video.artist_ids
    assert video.composers == 'Duy Anh'

    with pytest.raises(InvalidQualityError):
        video.download(temp_dir.name, -1)
    with pytest.raises(InvalidQualityError):
        video.download(temp_dir.name, 5)
    
    assert video.download(temp_dir.name, 0)
    assert video.download(temp_dir.name, 4)


def test_video2():
    video = Video('vs3zvdrrq12maa')
    assert video.video_title == 'Đôi Mắt'
    assert video.artists_name == 'Wanbi Tuấn Anh'
    assert video.composers == 'Nguyễn Hải Phong'
    assert 'zssmc36qq8vwke' in video.artist_ids
    assert video.published_year == 2009

    assert video.download(temp_dir.name, 3)
    assert video.download(temp_dir.name, 2)
    assert video.download(temp_dir.name, 1)

def test_video3():
    with pytest.raises(NotFoundError):
        Video('vs3zvdrrq12maaa')
