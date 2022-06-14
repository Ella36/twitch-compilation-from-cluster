#!/usr/bin/python3
# 1. Update clusters
# 2. Scrape find clips from creators or clusters
# 3. Select clips from creators or cluster
# 4. Download the clips
# 5. Format Download to Input. Draw text if needed
# 6. Merge to MP4
# 7. Publish and Update database 
import argparse

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
    parser.add_argument('--days', default='7', help='ex. 7 or 30')
    # Select clips
    parser.add_argument("--cont", action="store_true", help="continue selection from urls.txt")
    parser.add_argument('--duration', default='610', help='duration in seconds')
    parser.add_argument('--published_ok', action='store_true', help='set to include clips that have already been published')
    # Downloader
    parser.add_argument("--resolution", default='720')
    # Input formatter
    parser.add_argument("--skip_draw", action="store_true")
    parser.add_argument("--download", default='./download')
    parser.add_argument("--input", default='./input')
    # Merger
    parser.add_argument("--build", default='./build')
    parser.add_argument("--output", default='./output')
    return parser.parse_args()

if __name__ == '__main__':
    args = argparser()
    if is_prompt_confirm('Find Creator clips'):
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
    if is_prompt_confirm('write title description to title.txt'):
        write_title_description.write(args)