from tempfile import TemporaryDirectory
from pathlib import Path
import sys
sys.path.append('./')

import pytest
from model.exceptions import *

from model.track import Track


temp_dir = TemporaryDirectory()


def test_track1():
    track = Track('ts3w7z5wq9t1h9')
    assert track.song_title == 'Lặng Yêu'
    assert track.artists_name == 'Từ Minh Hy & Khánh Phương'
    assert 'zss7twqsqtf9e4' in track.artist_ids and 'zsswzmq7q918et' in track.artist_ids
    assert track.composers == 'Duy Anh'
    assert track.published_year == 2008
    assert track.album == 'Hoa Hồng Có Gai'
    assert track.album_id == 'xsswv5zqq92h1e'

    with pytest.raises(InvalidQualityError):
        track.download(temp_dir.name, -1)
    with pytest.raises(InvalidQualityError):
        track.download(temp_dir.name, 5)
    
    assert track.download(temp_dir.name, 0)
    assert track.download(temp_dir.name, 4)


def test_track2():
    track = Track('tsvd53cdqmhwvm')
    assert track.song_title == 'No Limit'
    assert track.artists_name == 'G-Eazy, A$AP Rocky & Cardi B'
    assert 'zssw07m5q9nt8h' in track.artist_ids and 'zsswz600q91knn' in track.artist_ids and 'zsswztqdq91fem' in track.artist_ids
    assert track.published_year == 2017
    assert track.album == 'No Limit (Single)'
    assert track.album_id == 'xss7tcmvqtfv82'

    with pytest.raises(InvalidQualityError):
        track.download(temp_dir.name, -1)
    with pytest.raises(InvalidQualityError):
        track.download(temp_dir.name, 5)
    
    assert track.download(temp_dir.name, 3)
    assert track.download(temp_dir.name, 2)
    assert track.download(temp_dir.name, 1)


def test_track3():
    track = Track('tsvq3zb5qew1qh')
    assert track.song_title == 'Em Yêu Ảo Lòi'
    assert track.artists_name == 'Yanbi, Da Vickie & T-akayz'
    assert 'zsswv0mzq92n81' in track.artist_ids and 'zssmwv75q892th' in track.artist_ids and 'zssmcc3tq8vvwf' in track.artist_ids
    assert track.published_year == 2012
    assert track.album == None
    assert track.album_id == None

    with pytest.raises(InvalidQualityError):
        track.download(Path(temp_dir.name), -1)
    with pytest.raises(InvalidQualityError):
        track.download(temp_dir.name, 5)
    
    assert track.download(temp_dir.name, 0)
    assert track.download(temp_dir.name, 2)
    assert track.download(temp_dir.name, 3)


def test_track4():
    with pytest.raises(NotFoundError):
        Track('tsvq3zb5qew1qh1')
