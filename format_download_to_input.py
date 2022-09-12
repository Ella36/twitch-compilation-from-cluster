#!/usr/bin/env python
from pathlib import Path
import subprocess
import shutil

from model.clips import Compilation, Element


def format_file(args, e: Element):
    input = e.filename
    target = e.filename_input
    # Add info to video before renaming
    if args.skip_draw:
        shutil.copy(input, target)
    else:
        text = f'{e.clip.creator.name} - {e.clip.title}'
        vf_string = f"fps=30,scale=-1:720,drawtext=fontfile=OpenSans-Regular.ttf:text='{text}':fontcolor=white:fontsize=48:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=10"
        subprocess.call([
            'ffmpeg',
            '-i', input,
            '-vf', vf_string,
            '-crf', '23', # optimize, higher is faster and lower quality [0-51]
            '-codec:a', 'copy',
            target
        ])

def clear_input_directory(args):
    for f in (args.wd / Path('./input')).glob('*'):
        f.unlink()

def format_download_to_input(args):
    clear_input_directory(args)
    compilation = Compilation.load(args.wd)
    for e in compilation:
        format_file(args, e)