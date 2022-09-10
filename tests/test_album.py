import sys
sys.path.append('./')

import pytest

from model.exceptions import *
from model.album import Album
from model.track import Track


def test_album1():
    a_id = 'xsswv5zqq92h1e'
    album = Album(a_id)
    assert album.album_name == 'Hoa Hồng Có Gai'
    assert album.year_published == 2008
    assert len(album.tracklist) == 10


def test_album2():
    a_id = 'xssmstv7q84f2t'
    album = Album(a_id)
    assert album.album_name == 'Im Lặng Và Ra Đi (Single)'
    assert album.year_published == 2016
    assert len(album.tracklist) == 1


def test_album3():
    with pytest.raises(NotFoundError):
        Track('xssmstv7q84f2ta')
