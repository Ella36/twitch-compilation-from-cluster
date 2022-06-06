#!/usr/bin/bash
i=0
for f in ./input/*.mp4
do
    echo "$f"
    ffmpeg -i $f -c copy -bsf:v h264_mp4toannexb -f mpegts "./build/$i.ts"
    ((i += 1))
done

ffmpeg -i "concat:fileIntermediate1.ts|fileIntermediate2.ts" -c copy -bsf:a aac_adtstoasc mergedVideo.mp4


