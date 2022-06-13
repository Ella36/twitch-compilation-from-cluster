#!/usr/bin/python3
# Merge files (.mp4) from /input to a single merged (.mp4) in /output
# clears /build directory for intermediate files
from pathlib import Path
import argparse
import subprocess


def clear_build_directory(args):
    # Clear BUILD directory of files
    for f in Path(args.build).glob('*'):
        f.unlink()

def convert_mp4_to_ts(args):
    # Convert mp4 to intermediate TS
    for i, f in enumerate(sorted(Path(args.input).glob('*.mp4'))):
        print(i, f)
        subprocess.call([
            'ffmpeg',
            '-i', f,
            '-c', 'copy',
            '-bsf:v', 'h264_mp4toannexb',
            '-f', 'mpegts',
            Path(args.build) / f'{i}.ts',
        ])


def merge_ts_to_mp4(args):
    # Merge TS into MP4
    concat_string = 'concat:' + '|'.join(map(lambda x: str(x), Path(args.build).glob('*.ts')))
    subprocess.call([
        'ffmpeg', 
        '-i', concat_string,
        '-c', 'copy',
        '-bsf:a', 'aac_adtstoasc',
        Path(args.output) / 'merged.mp4',
    ])

def merge_input_to_output(args):
    clear_build_directory(args)
    convert_mp4_to_ts(args)
    merge_ts_to_mp4(args)
    clear_build_directory(args)

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", default='./download')
    parser.add_argument("--input", default='./input')
    parser.add_argument("--build", default='./build')
    parser.add_argument("--output", default='./output')
    return parser.parse_args()

if __name__ == "__main__":
    args = argparser()
    merge_input_to_output(args)