#!/usr/bin/python
# Download files from urls.txt
#youtube-dl -a urls.txt -f 720 -o "download/%(autonumber)03d-%(creator)s-%(title)s-%(upload_date)s.%(ext)s"
import subprocess

from model.clips import Compilation
from model.mydb import Mydb


def download_clips(args) -> bool:
    compilation = Compilation.load(args.wd)
    # Temporary lock as published
    db = Mydb()
    for element in compilation:
        db.set_publish_temp(element.clip.url)
    db.commit()
    db.close()
    is_error = False
    for element in compilation:
        if element.download:
            continue
        print(element.clip.to_string())
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
        if any(e in error for e in ('ERROR', 'TypeError')):
            element.error = True
            is_error = True
        else:
            element.download = True
    compilation.dump(args.wd)
    return is_error