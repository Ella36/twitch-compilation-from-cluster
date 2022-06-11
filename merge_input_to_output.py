#!/usr/bin/python3
# Merge files (.mp4) from /input to a single merged (.mp4) in /output
# clears /build directory for intermediate files
import subprocess
from pathlib import Path

INPUT = Path('./input')
BUILD = Path('./build')
OUTPUT = Path('./output')

def clear_build_directory():
    # Clear BUILD directory of files
    for f in BUILD.glob('*'):
        f.unlink()


def convert_mp4_to_ts():
    # Convert mp4 to intermediate TS
    for i, f in enumerate(sorted(INPUT.glob('*.mp4'))):
        print(i, f)
        subprocess.call([
            'ffmpeg',
            '-i', f,
            '-c', 'copy',
            '-bsf:v', 'h264_mp4toannexb',
            '-f', 'mpegts',
            BUILD / f'{i}.ts',
        ])


def merge_ts_to_mp4():
    # Merge TS into MP4
    concat_string = 'concat:' + '|'.join(map(lambda x: str(x), BUILD.glob('*.ts')))
    subprocess.call([
        'ffmpeg', 
        '-i', concat_string,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        OUTPUT / 'merged.mp4',
    ])

def main():
    clear_build_directory()
    convert_mp4_to_ts()
    merge_ts_to_mp4()
    clear_build_directory()

if __name__ == '__main__':
    main()
