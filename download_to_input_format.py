#!/usr/bin/python3
import subprocess
from pathlib import Path
from datetime import datetime
import argparse

DOWNLOAD = Path('./download')
INPUT = Path('./input')

def format_download_to_input(args):
    # Clear INPUT directory of files
    for f in INPUT.glob('*'):
        f.unlink()

    # Format DOWNLOAD files to INPUT
    for _, f in enumerate(sorted(DOWNLOAD.glob('*.mp4'))):
        split = f.stem.strip().split('-')
        number = split[0]
        creator = split[1]
        title = '-'.join(split[2:-1])
        date = split[-1]
        date = datetime.strptime(date, '%Y%m%d').strftime("%d %B")
        formatted_filename = '-'.join(str(f.stem).split('-')[:-1]).strip() + '.mp4'
        target = INPUT / Path(formatted_filename)
        # Add info to video before renaming
        if args.skip_draw:
           f.rename(target)
        else:
            text = f'{creator} - {title}'
            #text = f'{creator} - {title} - {date}'
            vf_string = f"fps=30,scale=-1:720,drawtext=fontfile=/path/to/font.ttf:text='{text}':fontcolor=white:fontsize=48:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=10"
            #vf_string = f"drawtext=fontfile=/path/to/font.ttf:text='{text}':fontcolor=white:fontsize=48:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=10"
            subprocess.call([
                'ffmpeg', 
                '-i', f,
                '-vf', vf_string,
                '-crf', '32', # optimize, higher is faster and lower quality
                '-codec:a', 'copy',
                target,
            ])

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip_draw", action="store_true")
    return parser.parse_args()

if __name__ == "__main__":
    args = argparser()
    format_download_to_input(args)
