#!/usr/bin/python3
from datetime import datetime
from pathlib import Path
import argparse
import subprocess
import shutil

DELIMITER = '-KjFAn-ST-'

class InputFile:
    def __init__(self, f: Path):
        split = f.stem.strip().split(DELIMITER)
        self.number = split[0]
        self.creator = split[1]
        self.title = DELIMITER.join(split[2:-1])
        _date = split[-1]
        self.date = datetime.strptime(_date, '%Y%m%d').strftime("%d %B")
        self.filename = DELIMITER.join(str(f.stem).split(DELIMITER)[:-1]).strip() + '.mp4'

def format_file(args, f: Path):
    input = InputFile(f)
    target = args.wd / Path('./input') / input.filename
    # Add info to video before renaming
    if args.skip_draw:
        #rename
        shutil.copy(f, target)
    else:
        text = f'{input.creator} - {input.title}'
        vf_string = f"fps=30,scale=-1:720,drawtext=fontfile=/path/to/font.ttf:text='{text}':fontcolor=white:fontsize=48:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=10"
        subprocess.call([
            'ffmpeg', 
            '-i', f,
            '-vf', vf_string,
            '-crf', '32', # optimize, higher is faster and lower quality
            '-codec:a', 'copy',
            target
        ])

def clear_input_directory(args):
    for f in (args.wd / Path('./input')).glob('*'):
        f.unlink()

def format_download_to_input(args):
    clear_input_directory(args)
    for f in sorted((args.wd / Path('./download')).glob('*.mp4')):
        format_file(args, f)

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip_draw", action="store_true")
    parser.add_argument("--project", default='default')
    return parser.parse_args()

if __name__ == "__main__":
    args = argparser()
    args.wd = Path(args.project)
    format_download_to_input(args)
