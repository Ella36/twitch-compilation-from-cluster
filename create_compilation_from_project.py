#!/usr/bin/env python
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

from cfg.data import Project, PROJECTS
from download_clips import download_clips
from find_and_add_clips_to_db import find_and_add_clips_to_db
from format_download_to_input import format_download_to_input
from merge_input_to_output import merge_input_to_output
from model.clips import Compilation
from model.mydb import Mydb
from publish_compilation_to_db import publish
from select_clips_from_db import select_compilation_from_db, edit_compilation, load_compilation_from_published_project   
import write_title_description_thumbnail


def create_working_dir(args):
    wd = Path('proj-'+args.project)
    if wd.exists:
        if args.dir != "":
            wd = Path(str(wd)+'-'+args.dir)
        else:
            wd = Path(str(wd)+'-'+str(uuid.uuid4()).split('-')[0][:4])
    wd.mkdir(exist_ok=True)
    (wd / Path('./download')).mkdir(parents=True, exist_ok=True)
    (wd / Path('./input')).mkdir(parents=True, exist_ok=True)
    (wd / Path('./build')).mkdir(parents=True, exist_ok=True)
    # (wd / Path('./output')).mkdir(parents=True, exist_ok=True)
    (wd / Path('./thumbnail')).mkdir(parents=True, exist_ok=True)
    return wd

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
    # Use GUI for selecting/editing
    parser.add_argument('-g', '--gui', action='store_true', default=True, help='Use GUI')
    # Inputs
    parser.add_argument("--project", default="default", help="name of project, creates working directory")
    parser.add_argument("--dir", default="", help="suffix to project wd")
    parser.add_argument("--clip_ids", nargs='+', help="set if input are clip id ex AwkardHelpless... ")
    parser.add_argument("--load_compilation", action="store_true", help="loads compilation from pid and project name")
    parser.add_argument("--pid", help="used with load_compilation")
    return parser.parse_args()

def setup_args(args):
    project: Project = PROJECTS.by_name(args.project)
    print(f'Loading settings for Project :\n\t{project}')
    # Args we need to set
    args.wd = create_working_dir(args)
    args.title = project.title
    args.description = project.description
    args.days = project.days
    args.duration = project.duration
    args.categories = project.categories
    #args.clip_ids = project.clip_ids
    args.game_ids = project.game_ids
    args.clusters = project.clusters
    args.creators = project.creators
    args.lang = project.lang
    args.resolution = project.resolution
    args.published_ok = project.is_ok_already_published
    args.skip_draw = project.skip_draw
    args.youtube_category_id = project.youtube_category_id
    args.clip_urls = []
    if project.playlist_title == "untitled":
        args.playlist_title = False
    else:
        args.playlist_title = project.playlist_title
    if project.single:
        # Select only 1 clip
        args.single = True
        args.duration = 1
    else:
        args.single = False
    # Add clip_ids
    if args.clip_ids or args.load_compilation:
        args.clip_ids = args.clip_ids
        args.game_ids = [] 
        args.clusters = [] 
        args.creators = [] 
        args.published_ok = True
    print(f'Args set:\n\t{args}')
    return args

def sync_compilation_with_disk(args):
    compilation = Compilation.load(args.wd)
    compilation.sync_compilation_with_disk()

if __name__ == '__main__':
    # Load published
    args = argparser()
    args = setup_args(args)
    if args.load_compilation:
        db = Mydb()
        args.clip_urls = db.select_urls_from_project_and_pid(args.project, args.pid)
        db.close()
        if is_prompt_confirm('Add clips to DB'):
            find_and_add_clips_to_db(args)
        if is_prompt_confirm('Load compilation from project and pid'):
            load_compilation_from_published_project(args)
            print('Compilation loaded!')
        args.load_compilation = False
        args = setup_args(args)
        args.days = 9999
    if is_prompt_confirm('Find and add clips'):
        find_and_add_clips_to_db(args)
    if is_prompt_confirm('Select compilation from DB'):
        select_compilation_from_db(args)
        sync_compilation_with_disk(args)
    if is_prompt_confirm('Sync files'):
        sync_compilation_with_disk(args)
    if is_prompt_confirm('Download clips'):
        sync_compilation_with_disk(args)
        if download_clips(args):
            # Encountered error
            edit_compilation(args)
            sync_compilation_with_disk(args)
            if download_clips(args):
                edit_compilation(args)
                sync_compilation_with_disk(args)
                download_clips(args)
    if is_prompt_confirm('Edit compilation'):
        edit_compilation(args)
        sync_compilation_with_disk(args)
        if is_prompt_confirm('Download again clips'):
            download_clips(args)
            if is_prompt_confirm('Edit compilation'):
                edit_compilation(args)
                sync_compilation_with_disk(args)
                download_clips(args)
    sync_compilation_with_disk(args)
    if is_prompt_confirm('Format and Merge video'):
        format_download_to_input(args)
        merge_input_to_output(args)
    if is_prompt_confirm('Write title description'):
        write_title_description_thumbnail.write_title_and_json_meta(args)
    if is_prompt_confirm('Write thumbnail'):
        write_title_description_thumbnail.thumbnail(args)
    if is_prompt_confirm('Publish to DB!'):
        publish(args)
