#!/usr/bin/python3
# Merge files (.mp4) from /input to a single merged (.mp4) in /output
# clears /build directory for intermediate files
from pathlib import Path
import argparse
import subprocess
import uuid

DELIMITER = '-KjFAn-ST-'

def clear_build_directory(args):
    # Clear BUILD directory of files
    for f in (args.wd / Path('./build')).glob('*'):
        f.unlink()

import re
def convert_mp4_to_ts(args):
    # Convert mp4 to intermediate TS
    TIME = args.wd / Path('./time.txt')
    if TIME.exists():
        TIME.unlink()
    count = 0
    for i, f in enumerate(sorted((args.wd / Path('./input')).glob('*.mp4'))):
        p = subprocess.run([
            'ffmpeg',
            '-i', f,
            '-c', 'copy',
            '-bsf:v', 'h264_mp4toannexb',
            '-f', 'mpegts',
            args.wd / Path('./build') / f'{i:03d}.ts',
        ], capture_output=True, text=True)
        with TIME.open("a") as t:
            try:
                id, creator, title = [x.strip() for x in f.stem.split(DELIMITER)]
            except ValueError:
                print(f.stem)
                print(f.stem)
                print(f.stem)
            t.write(f'{int(count)};;{creator};;{title}\n')
            count += FFMPEGOutputToDurationInSeconds(p.stderr).duration

class FFMPEGOutputToDurationInSeconds:
    # 00:00:00.00 format 
    def __init__(self, str):
        m = re.search(r"time=(\d+):(\d+):(\d+.\d+)", str)
        self.hours = float(m.group(1))
        self.minutes = float(m.group(2))
        self.seconds = float(m.group(3))

    @property
    def duration(self) -> float:
        return self.hours * 3600 + self.minutes * 60 + self.seconds


def merge_ts_to_mp4(args):
    filename = args.wd.stem
    # Merge TS into MP4
    concat_string = 'concat:' + '|'.join(map(lambda x: str(x), sorted((args.wd / Path('./build')).glob('*.ts'))))
    subprocess.call([
        'ffmpeg', 
        '-i', concat_string,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        args.wd / f'{filename}.mp4',
    ])

def merge_input_to_output(args):
    clear_build_directory(args)
    convert_mp4_to_ts(args)
    merge_ts_to_mp4(args)
    #clear_build_directory(args)

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default='default')
    return parser.parse_args()

if __name__ == "__main__":
    args = argparser()
    args.wd = Path(args.project)
    merge_input_to_output(args)