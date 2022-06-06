https://ottverse.com/3-easy-ways-to-concatenate-mp4-files-using-ffmpeg/

Workflow
1. Gather links clips
    manually gather links to a .txt file
1. Download links (mp4)2a. Fix file names
    youtube-dl
    call from python or bash
1. Fix file names
1. Merge mp4
    See below. Bash or python. File names can be tricky
1. Upload mp4 to youtube/media something maybe

Repeat for as many

# Collecting download mp4

# Merging mp4 files
Method2 prefered

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

