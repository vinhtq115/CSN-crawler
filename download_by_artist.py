from argparse import ArgumentParser
from pathlib import Path

from model.track import Track
from model.artist import Artist
from model.utils import extract_id


def main(args):
    url = args.url
    output_dir = Path(args.output)
    quality = args.quality

    assert url.startswith('https://chiasenhac.vn/ca-si/')
    
    a_id = extract_id(url)
    artist = Artist(a_id)
    
    for track in artist.songs:
        Track(track).download(output_dir, quality)


if __name__ == '__main__':
    parser = ArgumentParser(description='Download tracks by artist from chiasenhac.vn.')
    parser.add_argument('url', type=str, help='Artist URL. Format: https://chiasenhac.vn/ca-si/')
    parser.add_argument('--output', '-o', type=str, help='Output directory', required=True)
    parser.add_argument('--quality', '-q', 
        type=int,
        help='Download quality. 0: FLAC, 1: M4A 500kbps, 2: MP3 320kbps, 3: MP3 128kbps, 4: M4A 32kbps.',
        default=0,
        choices=[0, 1, 2, 3, 4]
    )

    main(parser.parse_args())
