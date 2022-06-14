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

from find_creator_interval_urls import find_creator_interval_urls
from clip_selector import select_clips
from download_clips import download_clips
from download_to_input_format import format_download_to_input
from merge_input_to_output import merge_input_to_output
import write_title_description
from publish import publish




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
    # Search for clips
    parser.add_argument('cluster', nargs='+', default='cluster1', help='clustername ex. cluster1')
    parser.add_argument("--creators", action="store_true", help="set if list of creators")
    parser.add_argument("--category", action="store_true", help="set if input is category ex 'Just Chatting'")
    parser.add_argument("--days", default="30", help="pick n days")
    parser.add_argument("--project", default="default", help="name of project, creates working directory")
    # Select clips
    parser.add_argument("--cont", action="store_true", help="continue selection from urls.txt")
    parser.add_argument('--duration', default='610', help='duration in seconds')
    parser.add_argument('--published_ok', action='store_true', help='set to include clips that have already been published')
    parser.add_argument('--lang', default='en', help='set language ex. en, fr, es, ko')
    # Downloader
    parser.add_argument("--resolution", default='720')
    # Input formatter
    parser.add_argument("--skip_draw", action="store_true")
    # Merger
    return parser.parse_args()

def create_working_dir(wd):
    wd = Path(wd)
    wd.mkdir(exist_ok=True)
    (wd / Path('./download')).mkdir(parents=True, exist_ok=True)
    (wd / Path('./input')).mkdir(parents=True, exist_ok=True)
    (wd / Path('./build')).mkdir(parents=True, exist_ok=True)
    (wd / Path('./output')).mkdir(parents=True, exist_ok=True)
    (wd / Path('./thumbnail')).mkdir(parents=True, exist_ok=True)

if __name__ == '__main__':
    args = argparser()
    if args.project == "default":
        args.project = str(uuid.uuid4())
    create_working_dir(args.project)
    args.wd = Path(args.project)

    if is_prompt_confirm('Find clips'):
        find_creator_interval_urls(args)
    if is_prompt_confirm('Select Clips'):
        select_clips(args)
    if is_prompt_confirm('Download Clips'):
        download_clips(args)
    if is_prompt_confirm('Format download to Input Clips'):
        format_download_to_input(args)
    if is_prompt_confirm('Merge input to output'):
        merge_input_to_output(args)
    if is_prompt_confirm('Publish script to DB'):
        publish(args)
    if is_prompt_confirm('Write title description to title.txt'):
        write_title_description.write(args)
    if is_prompt_confirm('Montage thumbnail'):
        write_title_description.thumbnail(args)