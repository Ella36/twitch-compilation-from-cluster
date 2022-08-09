#!/usr/bin/env python
# Merge files (.mp4) from /input to a single merged (.mp4) in /output
# clears /build directory for intermediate files
from pathlib import Path
import re
import subprocess

from model.clips import Compilation

DELIMITER = "@;>>;@^_^@;<<@;"

def clear_build_directory(args):
    # Clear BUILD directory of files
    for f in (args.wd / Path('./build')).glob('*'):
        f.unlink()

def convert_mp4_to_ts(args):
    # Convert mp4 to intermediate TS
    TIME = args.wd / Path('./time.txt')
    if TIME.exists():
        TIME.unlink()
    count = 0
    compilation = Compilation.load(args.wd)
    compilation.order_clips()
    for e in compilation:
        f = Path(e.filename_input)
        p = subprocess.run([
            'ffmpeg',
            '-i', f,
            '-c', 'copy',
            '-bsf:v', 'h264_mp4toannexb',
            '-f', 'mpegts',
            e.filename_build_ts,
        ], capture_output=True, text=True)
        with TIME.open("a") as t:
            creator, title = e.clip.creator.name, e.clip.title
            t.write(f'{int(count)}{DELIMITER}{creator}{DELIMITER}{title}\n')
            # Sometimes doesn't print duration, use clip duration instead
            # count += FFMPEGOutputToDurationInSeconds(p.stderr).duration
            count += e.clip.duration

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
        '-y', # Overwrite if exists
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        args.wd / Path(f'{filename}.mp4'),
    ])

def merge_input_to_output(args):
    clear_build_directory(args)
    convert_mp4_to_ts(args)
    merge_ts_to_mp4(args)
