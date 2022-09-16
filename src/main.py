import os
from dotenv import load_dotenv

# for convenient debug, has no effect in production
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

import supervisely as sly
from supervisely.app.widgets import (
    Card,
    Container,
    Video,
    DatasetThumbnail,
)
import src.globals as g
import src.ui.input_dataset as input_dataset
import src.ui.select_tag as select_tag

# @TODO:
# https://yaytext.com/emoji/keycaps/
# emoji as step number 1️⃣

# 1. input dataset  # 2. select tag
# Select pair of videos - you can choose single video for dual layout
# First video for segmenta start # Second video for segment end
# start labeling button
# finish labeling button

# key-value:str tag has to be already created
# save user_id in final tagging
# video selector - simple selector - or searchable table with some marks - like started, number of tags, etc? - collapsable card with hide option
# input_dataset = os.environ[""]
# if multiple users use the same app with the same project


settings = Container(
    [input_dataset.layout, select_tag.layout], direction="horizontal", gap=15, fractions=[1, 1]
)

vid1 = 3267369
vid2 = 3267370
v1 = Video(vid1)
v2 = Video(vid2)
card1 = Card("Input video #1", "Select first video", content=v1)
card2 = Card("Input video #2", "Select second video", content=v2)

input_cards = Container(widgets=[card1, card2], direction="horizontal", gap=15, fractions=[1, 1])

card = Card("Tagging", "Description")
layout = Container(widgets=[settings, input_cards, card], direction="vertical", gap=15)

app = sly.Application(layout=layout)  # input_tag)  # layout)
