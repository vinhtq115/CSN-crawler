import random
import sys
sys.path.append('./')

import pytest

from model.exceptions import *
from model.artist import Artist
from model.track import Track


def test_artist1():
    a_id = 'zsswzmq7q918et'
    artist = Artist(a_id)
    assert artist.artist_name == 'Khánh Phương'
    assert artist.artist_id_number == 3524
    assert len(artist.songs) > 16 * 20
    
    song = Track(random.choice(list(artist.songs)))
    assert a_id in song.artist_ids


def test_artist2():
    a_id = 'zss7twqsqtf9e4'
    artist = Artist(a_id)
    assert artist.artist_name == 'Từ Minh Hy'
    assert artist.artist_id_number == 76999
    assert len(artist.songs) >= 11
    
    song = Track(random.choice(list(artist.songs)))
    assert a_id in song.artist_ids


def test_track4():
    with pytest.raises(NotFoundError):
        Track('zsswzmq7q918etz')
