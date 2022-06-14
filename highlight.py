#!/usr/bin/python3

twitch_credentials = {
   "client_id": "3v7w9gbeuaz6d6hiwlk448nw7lrsl3",
   "client_secret": "n23yzkko4ewa4oguwx962pkbg55uby"
}

acr_credentials = {
   "access_key": "m73k42t5v1jttq2h4h1r41v450lgqdpl",
   "secret_key": "1haPnq6StnU6S4FqoqzOvNAzLkapbaFeG7Pj945U",
   "host": "identify-eu-west-1.acrcloud.com"
}

from twitch_highlights import TwitchHighlights
from datetime import datetime, timedelta

started_at = datetime.utcnow() - timedelta(days=7)      # Starting date/time for included clips. Currently set to one week ago.
ended_at = datetime.utcnow() - timedelta(days=1)        # Ending date/time for included clips. Currently set to one week ago.

highlight_generator = TwitchHighlights(twitch_credentials=twitch_credentials)

highlight_generator.make_video_by_category(category="Fortnite", output_name="epic_highlight_video",
                                           language="fr", video_length=100, started_at=started_at,
                                           ended_at=ended_at,
                                           sort_by="chronologically")