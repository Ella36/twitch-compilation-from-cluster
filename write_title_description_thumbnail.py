#!/usr/bin/python3
from pathlib import Path
import subprocess
import requests

from InquirerPy import prompt

from model.mydb import Mydb
from model.clips import Compilation

def parse_time_file(args):
    def _filter_description(d):
        return d.replace('<3', ' ❤ ').replace('>', '').replace('<', '')
    TIME = args.wd / Path('./time.txt')
    text = TIME.read_text().strip().split('\n')
    description = f'{args.description}\n'
    # Description
    creators = []
    for t in text:
        seconds, creator, title = t.split(';;')
        creators.append(creator)
        seconds = f'{int(seconds)//60:02d}:{int(seconds)%60:02d}'
        creator_url = f'https://twitch.tv/{creator}'
        d =  """{} {:15} {}\n""".format(seconds, creator_url, title)
        description += _filter_description(d)
    # Title
    cmi = list(set(creators))
    compilation_number = new_compilation_number(args)
    # Set compilation number
    compilation = Compilation.load(args.wd)
    compilation.pid = compilation_number
    compilation.dump(args.wd)

    title_prefix = "#Twitch Compilation {} #{:03d}".format(args.title, compilation_number)
    if len(cmi) == 1:
        title = """{} {}""".format(title_prefix, cmi[0])
        if args.single:
            for t in text:
                _, _, title = t.split(';;')
                title = _filter_description(title)
            title = "#Twitch Compilation {} #{:03d} {}".format(args.title, compilation_number, title)
    elif len(cmi) == 2:
        title = """{} {} {}""".format(title_prefix, cmi[0], cmi[1])
    else:
        creators_prefix = "{} ".format(title_prefix)
        creators_names = [cmi[0], cmi[1]]
        for name in cmi[2:]:
            temp = creators_names[:]
            temp.append(name)
            if len(', '.join(temp)) + len(creators_prefix) < 95:
                creators_names.append(name)
            else:
                break
        title = creators_prefix + ', '.join(creators_names) + ', ...'
    keywords = ['#twitch', '#compilation', f'#{args.title}'] + [f'#{c}' for c in cmi]
    return title, description, keywords


from datetime import datetime, date
def _publish_date_formatted():
    # Next day 5PM
    today = date.today()
    tomorrow = datetime(today.year, today.month, today.day+1)
    tomorrow_16_30 = tomorrow.replace(hour=16, minute=30)
    return tomorrow_16_30.strftime("%Y-%m-%dT%H:%M:%S+02:00")

def _record_date_formatted():
    return datetime.now().strftime("%Y-%m-%d")

import json
def write_title_and_json_meta(args):
    title, description, keywords = parse_time_file(args)
    # Write Title
    keywords_format = ', '.join(keywords)
    out = title + '\n\n' + description + '\n' + keywords_format
    print(out)
    with (args.wd / Path('./title.txt')).open("w+") as f:
        f.write(out)
    # Write Meta JSON
    meta = {}
    meta["title"] = title
    meta["description"] = description
    meta["tags"] = keywords
    meta["privacyStatus"] = "private"
    meta["madeForKids"] = False
    meta["embeddable"] = True
    meta["publicStatsViewable"] = True
    meta["publishAt"] = _publish_date_formatted()
    meta["categoryId"] = args.youtube_category_id
    meta["recordingdate"] = _record_date_formatted()
    if args.playlist_title:
        meta["playlistTitles"] = [args.playlist_title]
    meta["language"] = args.lang
    # Writing to sample.json
    json_object = json.dumps(meta, indent = 4)
    META = args.wd / Path('./meta.json')
    with META.open("w") as f:
        f.write(json_object)

def new_compilation_number(args) -> int:
        db = Mydb()
        id = db.select_latest_compilation_number(args.project)
        id = int(id[0])+1 if id else 1
        db.con.close()
        return id

def thumbnail(args):
    compilation = Compilation.load(args.wd)
    thumbnail_urls = [element.clip.thumbnail_url for element in compilation] 
    # Download JPGs
    # Clear thumbnail dir
    for f in (args.wd / Path('./thumbnail')).glob('*'):
        f.unlink()
    def _download_jpg(image_name, url):
        r = requests.get(url, allow_redirects=True)
        with open(args.wd / Path(f'./thumbnail/{image_name}.jpg'), 'wb') as f:
            f.write(r.content)
    for i, u in enumerate(thumbnail_urls):
        _download_jpg(f'img{i+1:03d}', u)

    # Prompt for 4 JPGs
    choices = []
    for i, u in enumerate(thumbnail_urls):
        choice = {'name': f'img{i+1:03d}.jpg', 'value': f'img{i+1:03d}.jpg'}
        choices.append(choice)

    questions = [
        {
            'type': 'checkbox',
            'qmark': '😃',
            'message': 'Select thumbnail (4)',
            'name': 'img',
            'choices': choices
        }
    ]
    def _single_image_thumbnail():
        f = args.wd / Path(f'./thumbnail/img001.jpg')
        f.rename(args.wd / Path('thumbnail.jpg'))
        subprocess.call([
            #"""magick montage img*.jpg -geometry +1+1   montage_geom.jpg"""
            # magick composite thumbnail_overlay_pepega_pink_circle.png thumbnail.jpg out.jpg
            'magick',
            'composite',
            Path('./images/thumbnail_overlay_pepega_pink_circle_short.png'),
            args.wd / Path('thumbnail.jpg'),
            args.wd / Path('thumbnail_with_icon.jpg'),
        ])
    if args.single:
        _single_image_thumbnail()
        return
    thumbnail_folder = args.wd / Path('./thumbnail')
    print(f"Select clips from:\n\t{thumbnail_folder}")
    subprocess.call(['dolphin', thumbnail_folder])
    images = prompt(questions)['img']
    if len(images) == 1:
        _single_image_thumbnail()
        return
    if len(images) != 4:
        print('Select 4!')

    # Imagemagick create thumbnail
    subprocess.call([
        #"""magick montage img*.jpg -geometry +1+1   montage_geom.jpg"""
        'magick',
        'montage',
        args.wd / Path(f'./thumbnail/{images[0]}'),
        args.wd / Path(f'./thumbnail/{images[1]}'),
        args.wd / Path(f'./thumbnail/{images[2]}'),
        args.wd / Path(f'./thumbnail/{images[3]}'),
        '-tile', '2x2',
        '-geometry', '+1+1',
        args.wd / Path('thumbnail.jpg')
    ])
    # Imagemagick add Icon
    subprocess.call([
        #"""magick montage img*.jpg -geometry +1+1   montage_geom.jpg"""
        # magick composite thumbnail_overlay_pepega_pink_circle.png thumbnail.jpg out.jpg
        'magick',
        'composite',
        Path('./images/thumbnail_overlay_pepega_pink_circle.png'),
        args.wd / Path('thumbnail.jpg'),
        args.wd / Path('thumbnail_with_icon.jpg'),
    ])


if __name__ == '__main__':
    class argsT():
        def __init__(self):
            self.wd = None
            self.project = None
            self.single = None
            args.title = None
            args.description = None
    args = argsT()
    args.wd = Path('./asmr')
    args.project = "asmr"
    args.single = False
    args.description = "some description"
    args.title = "untitled"
    write_title_and_json_meta(args)
    #thumbnail(args)