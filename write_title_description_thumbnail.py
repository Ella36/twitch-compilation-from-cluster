#!/usr/bin/python3
from pathlib import Path
import subprocess
import requests

from InquirerPy import prompt

from model.mydb import Mydb
from model.clips import Compilation


def title_description(args):
    TIME = args.wd / Path('./time.txt')
    text = TIME.read_text().strip().split('\n')
    description = ''
    # Description
    creators = []
    for t in text:
        seconds, creator, title = t.split(';;')
        creators.append(creator)
        seconds = f'{int(seconds)//60:02d}:{int(seconds)%60:02d}'
        creator_url = f'https://twitch.tv/{creator}'
        description += """{} {:15} {}\n""".format(seconds, creator_url, title)
    # Title
    cmi = list(set(creators))
    compilation_number = new_compilation_number()

    if len(cmi) == 1:
        title = """#Twitch Compilation #{0:03d} {1}""".format(compilation_number, cmi[0])
    elif len(cmi) == 2:
        title = """#Twitch Compilation #{0:03d} {1} {2}""".format(compilation_number, cmi[0], cmi[1])
    else:
        prefix = "#Twitch Compilation #{0:03d} ".format(compilation_number)
        creators_names = [cmi[0], cmi[1]]
        for name in cmi[2:]:
            temp = creators_names[:]
            temp.append(name)
            if len(', '.join(temp)) + len(prefix) < 90:
                creators_names.append(name)
            else:
                break
        title = prefix + ', '.join(creators_names)
    out = title + '\n\n' + description
    print(out)
    with (args.wd / Path('./title.txt')).open("w+") as f:
        f.write(out)

def new_compilation_number() -> int:
        db = Mydb()
        id = db.select_latest_compilation_number()
        db.commit()
        db.con.close()
        return id+1


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
    print(f"Select clips from:\n\t{args.wd / Path('./thumbnail')}")
    images = prompt(questions)['img']
    if len(images) != 4:
        print('Select 4!')

    # Imagemagick create thumbnail
    subprocess.call([
        #"""magick montage img*.jpg -geometry +1+1   montage_geom.jpg"""
        'magick',
        'montage',
        args.wd / (f'./thumbnail/{images[0]}'),
        args.wd / (f'./thumbnail/{images[1]}'),
        args.wd / Path(f'./thumbnail/{images[2]}'),
        args.wd / Path(f'./thumbnail/{images[3]}'),
        '-tile 2x2',
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
    args = argsT()
    args.wd = Path('./pinktuber')
    title_description(args)
    thumbnail(args)