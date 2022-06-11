#!/usr/bin/bash
# Download files from urls.txt
youtube-dl -a urls.txt -f 720 -o "download/%(autonumber)03d-%(creator)s-%(title)s-%(upload_date)s.%(ext)s"
