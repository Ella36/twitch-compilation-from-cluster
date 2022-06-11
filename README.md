https://ottverse.com/3-easy-ways-to-concatenate-mp4-files-using-ffmpeg/

Workflow
1. Input cluster to be selected
1. Select cluster and add clip links to database
1. Filter valid/invalid clips
    compile clip links with help of algorithm
    prompt user here
    add script of links to database
1. Download links (mp4)
    Format file names, add statistic data
    youtube-dl
1. (optional) Add text overlay with title, creator
1. Merge mp4
    See below. Bash or python
    once merged, update links in database using script from earlier
    prompt, published videos table
    cluster, creators, date, URls, status (published, script)
1. Upload mp4 to youtube/media

Repeat for as many

## Clips
database
    records should contain:
        title, creator, date, link
        link is unique identifier
    clip added to a compilation bool

config file
    clusters 
        names of creator
        perhaps with weigth for clip selection = total amount of followers
    

## Method1
Slow re-encode mp4 then concatenate
```
ffmpeg -i file1.mp4 -i file2.mp4 -i file3.mp4 \
       -filter_complex "[0:v] [0:a] [1:v] [1:a] [2:v] [2:a]
                        concat=n=3:v=1:a=1 [vv] [aa]" \
       -map "[vv]" -map "[aa]" mergedVideo.mp4
```

## Method2
Faster to intermediate TransportStream files then concatenate to mp4
Requires temporary TS file cleanup

```
ffmpeg -i file1.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts fileIntermediate1.ts
```

```
ffmpeg -i "concat:fileIntermediate1.ts|fileIntermediate2.ts" -c copy -bsf:a aac_adtstoasc mergedVideo.mp4
```

## Add Text to top center
```
ffmpeg -i input.mp4 -vf "drawtext=fontfile=/path/to/font.ttf:text='Stack Overflow':fontcolor=white:fontsize=48:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=10" -codec:a copy output.mp4
```

