#!/usr/bin/python
# Download files from urls.txt
#youtube-dl -a urls.txt -f 720 -o "download/%(autonumber)03d-%(creator)s-%(title)s-%(upload_date)s.%(ext)s"
import argparse
import subprocess
from pathlib import Path


def download_clips(args):
    urls = Path('./urls.txt').read_text().strip().split('\n')
    i = 1
    errors = []
    delimiter = '-KjFAn-ST-'
    for u in urls:
        p = subprocess.run([
            'youtube-dl', 
            u,
            '-f', f'{args.resolution}',
            '-o', "download/{:03d}{}%(creator)s{}%(title)s{}%(upload_date)s.%(ext)s".format(i, delimiter, delimiter, delimiter),
        ],capture_output=True, text=True)
        i += 1
        print(p.stdout)
        print(p.stderr)
        error = p.stderr
        if 'ERROR' in error:
            errors.append(u)
    error_file = Path('./errors.txt')
    if error_file.exists():
        error_file.unlink()
    with error_file.open("w") as f:
        f.write('\n'.join(errors))

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", default='./download')
    parser.add_argument("--resolution", default='720')
    return parser.parse_args()

if __name__ == "__main__":
    args = argparser()
    download_clips(args)
