#!/usr/bin/python3
# 1. Update clusters
# 2. Scrape find clips from creators or clusters
# 3. Select clips from creators or cluster
# 4. Download the clips
# 5. Format Download to Input. Draw text if needed
# 6. Merge to MP4
# 7. Publish and Update database 
import argparse
from pathlib import Path
import uuid

from InquirerPy import prompt

from find_and_add_clips_to_db import find_and_add_clips_to_db
from select_clips_from_db import select_compilation_from_db, edit_compilation
from download_clips import download_clips
from format_download_to_input import format_download_to_input
from merge_input_to_output import merge_input_to_output
import write_title_description_thumbnail
from publish_compilation_to_db import publish
from model.clips import Compilation


def is_prompt_confirm(step: str):
    questions = [
        {
            'type': 'confirm',
            'message': f'Do you want to {step}?',
            'name': 'confirm',
            'default': True,
        },
    ]
    answers = prompt(questions)
    return answers['confirm']

def argparser():
    parser = argparse.ArgumentParser()
    # Inputs
    parser.add_argument("--cluster", nargs='+', help="clusterfile with name(s) of twitch channel (creator)")
    parser.add_argument("--creators", nargs='+', help="set if list of creators")
    parser.add_argument("--game_ids", nargs='+', help="set if input are game id ex 12345 ")
    parser.add_argument("--clip_ids", nargs='+', help="set if input are clip id ex AwkardHelpless... ")
    parser.add_argument("--categories", nargs='+', help="set if input is category ex 'Just Chatting'")
    # Database
    parser.add_argument('-co', '--compilations', action='store_true', help='create table compilations')
    parser.add_argument('-c', '--clips', action='store_true', help='create table clips')
    parser.add_argument('--sync', action='store_true', help='update published flag from compilations')
    # Confirm
    parser.add_argument("--confirm", action="store_true", help="autoconfirms")
    parser.add_argument("--single", action="store_true", help="single URL to skip select clips and publish")
    # Search for clips
    parser.add_argument("--days", default="30", help="pick n days")
    parser.add_argument("--dir", default="", help="suffix to append to project to create dir")
    # Select clips
    parser.add_argument("--project", default="default", help="name of project, creates working directory")
    parser.add_argument("--cont", action="store_true", help="continue selection from urls.txt")
    parser.add_argument('--duration', default='610', help='duration in seconds')
    parser.add_argument('--published_ok', action='store_true', help='set to include clips that have already been published')
    parser.add_argument('--lang', default='en', help='set language ex. en, fr, es, ko')
    # Downloader
    parser.add_argument("--resolution", default='720')
    # Input formatter
    parser.add_argument("--skip_draw", action="store_true")
    #
    parser.add_argument("--title", default="untitled", help="title part before numbers ex. Twitch Compilation -->(NA)<-- #001")
    parser.add_argument("--description", default="description not added", help="ex. Best twitch clips past 30 days!")
    # Merger
    return parser.parse_args()

def create_working_dir(args):
    wd = Path(args.project)
    if wd.exists:
        if args.dir != "":
            wd = Path(str(wd)+args.dir)
        else:
            wd = Path(str(wd)+str(uuid.uuid4()).split('-')[0])
    wd.mkdir(exist_ok=True)
    (wd / Path('./download')).mkdir(parents=True, exist_ok=True)
    (wd / Path('./input')).mkdir(parents=True, exist_ok=True)
    (wd / Path('./build')).mkdir(parents=True, exist_ok=True)
    # (wd / Path('./output')).mkdir(parents=True, exist_ok=True)
    (wd / Path('./thumbnail')).mkdir(parents=True, exist_ok=True)
    return wd

from model.mydb import Mydb
if __name__ == '__main__':
    args = argparser()
    if args.clips or args.compilations or args.sync:
        db = Mydb()
        if args.compilations and is_prompt_confirm('DELETE or CREATE compilations'):
            db.create_compilation()
        if args.clips and is_prompt_confirm('DELETE or CREATE clips'):
            db.create_clips()
        if args.sync:
           db.set_published_from_compilations()
           db.commit()
        db.close()
        exit(0)
    if args.project == "default":
        args.project = str(uuid.uuid4()).split('-')[0]
    args.wd = create_working_dir(args)

    if is_prompt_confirm('Find clips'):
        find_and_add_clips_to_db(args)
    if args.confirm or is_prompt_confirm('Select Clips for Compilation'):
        select_compilation_from_db(args)
    if args.confirm or is_prompt_confirm('Download Compilation Clips'):
        compilation = Compilation.load(args.wd)
        compilation.sync_compilation_with_disk()
        download_clips(args)
    if is_prompt_confirm('Edit Compilation'):
        edit_compilation(args)
    if is_prompt_confirm('Download again'):
        compilation = Compilation.load(args.wd)
        compilation.sync_compilation_with_disk()
        download_clips(args)
    if is_prompt_confirm('Sync compilation with disk'):
        compilation = Compilation.load(args.wd)
        compilation.sync_compilation_with_disk()
    if args.confirm or is_prompt_confirm('Format download to Input Clips'):
        format_download_to_input(args)
        merge_input_to_output(args)
    if args.confirm or is_prompt_confirm('Write title description to title.txt'):
        write_title_description_thumbnail.title_description(args)
        write_title_description_thumbnail.thumbnail(args)
    if is_prompt_confirm('Publish compilation to DB'):
        publish(args)