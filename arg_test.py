#!/usr/bin/python3
# 1. Update clusters
# 2. Scrape find clips from creators or clusters
# 3. Select clips from creators or cluster
# 4. Download the clips
# 5. Format Download to Input. Draw text if needed
# 6. Merge to MP4
# 7. Publish and Update database 
import argparse

def argparser():
    parser = argparse.ArgumentParser()
    # Search for clips
    parser.add_argument('--clusters', nargs='+', help='clustername ex. cluster1')
    parser.add_argument('--game_ids', nargs='+', help='clustername ex. cluster1')
    parser.add_argument('--clip_ids', nargs='+', help='clustername ex. cluster1')
    parser.add_argument('--categories', nargs='+', help='clustername ex. cluster1')
    return parser.parse_args()
if __name__ == '__main__':
    args = argparser()
    print(args)