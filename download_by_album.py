from argparse import ArgumentParser
from pathlib import Path

from model.track import Track
from model.album import Album
from model.utils import extract_id
from model.exceptions import NotFoundError


def main(args):
    url = args.url
    output_dir = Path(args.output)
    quality = args.quality

    assert url.startswith('https://chiasenhac.vn/nghe-album/')
    
    a_id = extract_id(url)
    album = Album(a_id)
    
    max_track_number = album.tracklist[-1]['number']
    width = len(str(max_track_number))

    for track in album.tracklist:
        try:
            _track = Track(track['id'])
            numbering = str(track['number']).zfill(width) + '. '
            _track.download(output_dir, quality, numbering)
        except NotFoundError:
            print(f'Skipped {_track.artists_name} - {_track.song_title} [{_track.track_id}] because no download link is available.')

if __name__ == '__main__':
    parser = ArgumentParser(description='Download tracks by album from chiasenhac.vn.')
    parser.add_argument('url', type=str, help='Album URL. Format: https://chiasenhac.vn/nghe-album/xxx.html')
    parser.add_argument('--output', '-o', type=str, help='Output directory', required=True)
    parser.add_argument('--quality', '-q', 
        type=int,
        help='Download quality. 0: FLAC, 1: M4A 500kbps, 2: MP3 320kbps, 3: MP3 128kbps, 4: M4A 32kbps.',
        default=0,
        choices=[0, 1, 2, 3, 4]
    )

    main(parser.parse_args())
