#!/usr/bin/python3
from pathlib import Path
import subprocess
import requests

from InquirerPy import prompt

from model.mydb import Mydb
from model.clips import Compilation


def title_description(args):
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

    if len(cmi) == 1:
        title = """#Twitch Compilation {2} #{0:03d} {1}""".format(compilation_number, cmi[0], args.title)
    elif len(cmi) == 2:
        title = """#Twitch Compilation {3} #{0:03d} {1} {2}""".format(compilation_number, cmi[0], cmi[1], args.title)
    else:
        prefix = "#Twitch Compilation {1} #{0:03d} ".format(compilation_number, args.title)
        creators_names = [cmi[0], cmi[1]]
        for name in cmi[2:]:
            temp = creators_names[:]
            temp.append(name)
            if len(', '.join(temp)) + len(prefix) < 95:
                creators_names.append(name)
            else:
                break
        title = prefix + ', '.join(creators_names) + ', ...'
    keywords = f'\n#twitch, #compilation, #{args.title}' + ', '.join([f'#{c}' for c in cmi])
    out = title + '\n\n' + description + keywords
    print(out)
    with (args.wd / Path('./title.txt')).open("w+") as f:
        f.write(out)
    compilation = Compilation.load(args.wd)
    compilation.pid = compilation_number
    compilation.dump(args.wd)

def new_compilation_number(args) -> int:
        db = Mydb()
        id = db.select_latest_compilation_number(args.project)
        if id:
            id = int(id[0])+1
        else:
            id = 1
        db.commit()
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
    title_description(args)
    #thumbnail(args)