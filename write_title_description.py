#!/usr/bin/python3
from pathlib import Path
import subprocess
import requests

from InquirerPy import prompt

from db.mydb import Mydb


def write():
    TIME = Path('./time.txt')
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
    script_number = last_index()

    if len(cmi) == 1:
        title = """#Twitch Compilation #{0:03d} {1})""".format(script_number, cmi[0])
    elif len(cmi) == 2:
        title = """#Twitch Compilation #{0:03d} {1} {2}""".format(script_number, cmi[0], cmi[1])
    else:
        prefix = "#Twitch Compilation #{0:03d} ".format(script_number)
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
    with Path('./title.txt').open("w+") as f:
        f.write(out)

def last_index() -> int:
        db = Mydb()
        id = db.select_latest_script_number()
        db.commit()
        db.con.close()
        return id


def thumbnail():
    URLS = Path('./urls.txt')
    text = URLS.read_text().strip().split('\n')
    db = Mydb()
    thumbnail_urls = []
    for url in text:
        # Find and download thumbnail
        uri = db.select_thumbnail_url(url)
        thumbnail_urls.append(uri)
    db.con.close()

    # Download JPGs
    # Clear thumbnail dir
    for f in Path('./thumbnail').glob('*'):
        f.unlink()
    def _download_jpg(image_name, url):
        r = requests.get(url, allow_redirects=True)
        with open(f'./thumbnail/{image_name}.jpg', 'wb') as f:
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
    images = prompt(questions)['img']
    if len(images) != 4:
        print('Select 4!')

    # Imagemagick
    subprocess.call([
        #"""magick montage img*.jpg -geometry +1+1   montage_geom.jpg"""
        'magick',
        'montage',
        f'./thumbnail/{images[0]}',
        f'./thumbnail/{images[1]}',
        f'./thumbnail/{images[2]}',
        f'./thumbnail/{images[3]}',
        '-geometry', '+1+1',
        'thumbnail.jpg'
    ])

if __name__ == '__main__':
    #thumbnail()
    write()