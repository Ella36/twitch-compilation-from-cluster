#!/usr/bin/python
# Download files from urls.txt
#youtube-dl -a urls.txt -f 720 -o "download/%(autonumber)03d-%(creator)s-%(title)s-%(upload_date)s.%(ext)s"
import argparse
import subprocess
from pathlib import Path

from model.clips import Compilation


def download_clips(args) -> bool:
    compilation = Compilation.load(args.wd)
    for element in compilation:
        print(element.clip.to_string())
        errors = []
        u = element.clip.url
        p = subprocess.run([
            'youtube-dl', 
            u,
            '-f', f'{args.resolution}',
            '-o', element.filename,
        ],capture_output=True, text=True)
        print(p.stdout)
        print(p.stderr)
        error = p.stderr
        if 'ERROR' in error:
            element.error = True
    compilation.dump(args.wd)
    return len(errors) > 0

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", default='./download')
    parser.add_argument("--resolution", default='720')
    parser.add_argument("--project", default='default')
    return parser.parse_args()

if __name__ == "__main__":
    args = argparser()
    args.wd = Path(args.project)
    download_clips(args)
