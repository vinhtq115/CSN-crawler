from argparse import ArgumentParser
from pathlib import Path

from model.track import Track
from model.utils import extract_id


def main(args):
    url = args.url
    output_dir = Path(args.output)
    quality = args.quality
    
    s_id = extract_id(url)
    Track(s_id).download(output_dir, quality)


if __name__ == '__main__':
    parser = ArgumentParser(description='Download single track from chiasenhac.vn.')
    parser.add_argument('url', type=str, help='Track URL')
    parser.add_argument('--output', '-o', type=str, help='Output directory', required=True)
    parser.add_argument('--quality', '-q', type=int, help='Download quality. 0: FLAC, 1: M4A 500kbps, 2: MP3 320kbps, 3: MP3 128kbps, 4: M4A 32kbps.', default=0)

    main(parser.parse_args())
