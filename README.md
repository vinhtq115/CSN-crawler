# CSN-crawler
For crawling music on chiasenhac.vn.

## Installation

Create a Python environment if not already have one (using `conda`). Then, install prerequisite using `pip`:

```
pip install -r requirements.txt
```

## Usage

### Download single track

```
usage: download_track.py [-h] --output OUTPUT [--quality {0,1,2,3,4}] url

positional arguments:
  url                   Track URL. Format: https://chiasenhac.vn/mp3/xxx.html

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output directory
  --quality {0,1,2,3,4}, -q {0,1,2,3,4}
                        Download quality. 0: FLAC, 1: M4A 500kbps, 2: MP3 320kbps, 3: MP3 128kbps, 4: M4A 32kbps.
```
Example:
```
python download_track.py -o output_dir -q 0 https://chiasenhac.vn/mp3/ngo-kien-huy-thu-thuy/dinh-menh-ta-gap-nhau-ts36t0tbqkfnfq.html
```

### Download album

```
usage: download_album.py [-h] --output OUTPUT [--quality {0,1,2,3,4}] url

positional arguments:
  url                   Album URL. Format: https://chiasenhac.vn/nghe-album/xxx.html

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output directory
  --quality {0,1,2,3,4}, -q {0,1,2,3,4}
                        Download quality. 0: FLAC, 1: M4A 500kbps, 2: MP3 320kbps, 3: MP3 128kbps, 4: M4A 32kbps.
```

Example:
```
python download_album.py -o output_dir -q 0 https://chiasenhac.vn/nghe-album/cham-tay-vao-dieu-uoc-xssmqqr0q8eean.html
```

### Download by artist

```
usage: download_by_artist.py [-h] --output OUTPUT [--quality {0,1,2,3,4}] url

positional arguments:
  url                   Artist URL. Format: https://chiasenhac.vn/ca-si/xxx.html

options:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output directory
  --quality {0,1,2,3,4}, -q {0,1,2,3,4}
                        Download quality. 0: FLAC, 1: M4A 500kbps, 2: MP3 320kbps, 3: MP3 128kbps, 4: M4A 32kbps.
```

Example:
```
python download_by_artist.py -o output_dir -q 0 https://chiasenhac.vn/ca-si/khanh-phuong-zsswzmq7q918et.html
```

## License
[MIT](https://choosealicense.com/licenses/mit/)