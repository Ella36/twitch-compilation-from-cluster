#!/usr/bin/env python
from datetime import datetime, date, timedelta
from pathlib import Path
import json
import requests
import subprocess

from InquirerPy import prompt

from model.mydb import Mydb
from model.clips import Compilation

DELIMITER = "@;>>;@^_^@;<<@;"

def parse_time_file(args):
    def _filter_description(d):
        return d.replace('<3', ' ❤ ').replace('>', '').replace('<', '')
    TIME = args.wd / Path('./time.txt')
    text = TIME.read_text().strip().split('\n')
    description = f'{args.description}\n'
    # Description
    creators = []
    for t in text:
        try:
            seconds, creator, title = t.split(DELIMITER)
        except ValueError:
            print(f"ValueError: {t}")
            continue
        creators.append(creator)
        seconds = f'{int(seconds)//60:02d}:{int(seconds)%60:02d}'
        creator_url = f'https://twitch.tv/{creator}'
        d =  """{} {:15} {}\n""".format(seconds, creator_url, title)
        description += _filter_description(d)
    # Title
    cmi = list(set(creators))
    # Set compilation number
    compilation = Compilation.load(args.wd)
    try:
        pid = int(args.pid)
    except (AttributeError, TypeError):
        pid = new_pid(args)
    compilation.pid = pid
    compilation.dump(args.wd)

    title_prefix = "#Twitch Compilation {} #{:03d}".format(args.title, pid)
    if len(cmi) == 1:
        title = """{} {}""".format(title_prefix, cmi[0])
        if args.single:
            for t in text:
                try:
                    _, _, title = t.split(DELIMITER)
                except ValueError:
                    print(f"ValueError: {t}")
                    title = ""
                title = _filter_description(title)
            title = "#Twitch Compilation {} #{:03d} {}".format(args.title, pid, title)
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
    description_postfix_file = Path('description_postfix.txt')
    description_postfix = description_postfix_file.read_text()
    description += '\n'+description_postfix+'\n'
    return title, description, keywords

def prompt_for_date():
    def prompt_choices_publish_date():
        def _gen_choices() -> list:
            def _to_choice_format(date):
                name = date.strftime('%-d/%m, %H:%M')
                value = date
                return {'name': name, 'value': value}
            now = datetime.utcnow()
            time_in_1_day = now + timedelta(days=1)
            time_in_2_days = now + timedelta(days=2)
            time_in_3_days = now + timedelta(days=3)
            time_in_4_days = now + timedelta(days=4)
            time_in_5_days = now + timedelta(days=5)
            time_in_6_days = now + timedelta(days=6)
            time_in_7_days = now + timedelta(days=7)
            time_in_8_days = now + timedelta(days=8)
            time_in_9_days = now + timedelta(days=9)
            time_in_10_days = now + timedelta(days=10)
            today_12_00 = now.replace(hour=12, minute=0, second=0, microsecond=0)
            today_16_30 = now.replace(hour=16, minute=30, second=0, microsecond=0)
            today_15_30 = now.replace(hour=15, minute=30, second=0, microsecond=0)
            tomorrow_12_00 = time_in_1_day.replace(hour=12, minute=0, second=0, microsecond=0)
            tomorrow_16_30 = time_in_1_day.replace(hour=16, minute=30, second=0, microsecond=0)
            tomorrow_15_30 = time_in_1_day.replace(hour=15, minute=30, second=0, microsecond=0)
            day_after_tomorrow_15_30 = time_in_2_days.replace(hour=15, minute=30, second=0, microsecond=0)
            day_after_tomorrow_16_30 = time_in_2_days.replace(hour=16, minute=30, second=0, microsecond=0)
            day_after_tomorrow_12_00 = time_in_2_days.replace(hour=12, minute=00, second=0, microsecond=0)
            day_plus_3_15_30 = time_in_3_days.replace(hour=15, minute=30, second=0, microsecond=0)
            day_plus_3_16_30 = time_in_3_days.replace(hour=16, minute=30, second=0, microsecond=0)
            day_plus_3_12_00 = time_in_3_days.replace(hour=12, minute=00, second=0, microsecond=0)

            day_plus_4_15_30 = time_in_4_days.replace(hour=15, minute=30, second=0, microsecond=0)
            day_plus_4_16_30 = time_in_4_days.replace(hour=16, minute=30, second=0, microsecond=0)
            day_plus_4_12_00 = time_in_4_days.replace(hour=12, minute=00, second=0, microsecond=0)

            day_plus_5_15_30 = time_in_5_days.replace(hour=15, minute=30, second=0, microsecond=0)
            day_plus_5_16_30 = time_in_5_days.replace(hour=16, minute=30, second=0, microsecond=0)
            day_plus_5_12_00 = time_in_5_days.replace(hour=12, minute=00, second=0, microsecond=0)

            day_plus_6_15_30 = time_in_6_days.replace(hour=15, minute=30, second=0, microsecond=0)
            day_plus_6_16_30 = time_in_6_days.replace(hour=16, minute=30, second=0, microsecond=0)
            day_plus_6_12_00 = time_in_6_days.replace(hour=12, minute=00, second=0, microsecond=0)

            day_plus_7_15_30 = time_in_7_days.replace(hour=15, minute=30, second=0, microsecond=0)
            day_plus_7_16_30 = time_in_7_days.replace(hour=16, minute=30, second=0, microsecond=0)
            day_plus_7_12_00 = time_in_7_days.replace(hour=12, minute=00, second=0, microsecond=0)


            day_plus_8_15_30 = time_in_8_days.replace(hour=15, minute=30, second=0, microsecond=0)
            day_plus_8_16_30 = time_in_8_days.replace(hour=16, minute=30, second=0, microsecond=0)
            day_plus_8_12_00 = time_in_8_days.replace(hour=12, minute=00, second=0, microsecond=0)

            day_plus_9_15_30 = time_in_9_days.replace(hour=15, minute=30, second=0, microsecond=0)
            day_plus_9_16_30 = time_in_9_days.replace(hour=16, minute=30, second=0, microsecond=0)
            day_plus_9_12_00 = time_in_9_days.replace(hour=12, minute=00, second=0, microsecond=0)

            day_plus_10_15_30 = time_in_10_days.replace(hour=15, minute=30, second=0, microsecond=0)
            day_plus_10_16_30 = time_in_10_days.replace(hour=16, minute=30, second=0, microsecond=0)
            day_plus_10_12_00 = time_in_10_days.replace(hour=12, minute=00, second=0, microsecond=0)

            dates_in_choice_order = [
                tomorrow_15_30, tomorrow_16_30, tomorrow_12_00,
                day_after_tomorrow_15_30, day_after_tomorrow_16_30, day_after_tomorrow_12_00,
                today_15_30, today_16_30, today_12_00,
                day_plus_3_15_30, day_plus_3_16_30, day_plus_3_12_00,
                day_plus_4_15_30, day_plus_4_16_30, day_plus_4_12_00,
                day_plus_5_15_30, day_plus_5_16_30, day_plus_5_12_00,
                day_plus_6_15_30, day_plus_6_16_30, day_plus_6_12_00,
                day_plus_7_15_30, day_plus_7_16_30, day_plus_7_12_00,
                day_plus_8_15_30, day_plus_8_16_30, day_plus_8_12_00,
                day_plus_9_15_30, day_plus_9_16_30, day_plus_9_12_00,
                day_plus_10_15_30, day_plus_10_16_30, day_plus_10_12_00
            ]
            choices = list(map(_to_choice_format, dates_in_choice_order))
            return choices
        choices = _gen_choices()
        questions = [
            {
                'type': 'checkbox',
                'qmark': '😃',
                'message': 'Select date option',
                'name': 'date_option',
                'choices': choices
            }
        ]
        answers = prompt(questions)['date_option']
        return answers[0] if len(answers) > 0 else choices[0]['value']
    return prompt_choices_publish_date()

def _publish_date_formatted():
    return prompt_for_date().strftime("%Y-%m-%dT%H:%M:%S+02:00")

def _record_date_formatted():
    return datetime.now().strftime("%Y-%m-%d")

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

def new_pid(args) -> int:
        db = Mydb()
        id = db.select_latest_pid(args.project)
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
            Path('./images/thumbnail_overlay_single.png'),
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
        Path('./images/thumbnail_overlay.png'),
        args.wd / Path('thumbnail.jpg'),
        args.wd / Path('thumbnail_with_icon.jpg'),
    ])
