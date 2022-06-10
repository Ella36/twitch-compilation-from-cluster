#!/usr/bin/python3
# Merge files (.mp4) from /input to a single merged (.mp4) in /output
# clears /build directory for intermediate files
import subprocess
from pathlib import Path

INPUT = Path('./input')
BUILD = Path('./build')
OUTPUT = Path('./output')

def main():
    # Clear BUILD directory of files
    for f in BUILD.glob('*'):
        f.unlink()

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

    # Merge TS into MP4
    concat_string = 'concat:' + '|'.join(map(lambda x: str(x), BUILD.glob('*.ts')))
    subprocess.call([
        'ffmpeg', 
        '-i', concat_string,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        OUTPUT / 'merged.mp4',
    ])

    # Clear BUILD directory of files
    for f in BUILD.glob('*'):
        f.unlink()

if __name__ == '__main__':
    main()
