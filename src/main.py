import os
from dotenv import load_dotenv

# for convenient debug, has no effect in production
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

import supervisely as sly
from supervisely.app.widgets import Card, Container, VideoThumbnail
import src.globals as g
import src.ui.input_dataset as input_dataset
import src.ui.select_tag as select_tag
import src.ui.select_videos as select_videos
import src.ui.left_video as left_video
import src.ui.right_video as right_video
import src.ui.tagging as tagging

# @TODO:
# https://yaytext.com/emoji/keycaps/
# emoji as step number 1️⃣

# 1. input dataset  # 2. select tag
# Select pair of videos - you can choose single video for dual layout
# First video for segmenta start # Second video for segment end
# start labeling button
# finish labeling button

# save user_id in final tagging (use user api token to tag videos)
# if multiple users use the same app with the same project

settings = Container(
    [input_dataset.layout, select_tag.layout], direction="horizontal", gap=15, fractions=[1, 1]
)


input_cards = Container(
    widgets=[left_video.card, right_video.card], direction="horizontal", gap=15, fractions=[1, 1]
)

layout = Container(
    widgets=[settings, select_videos.card, input_cards, tagging.layout],
    direction="vertical",
    gap=15,
)

app = sly.Application(layout=layout)
select_videos.build_table()
