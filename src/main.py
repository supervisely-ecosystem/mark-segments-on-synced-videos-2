import os
from dotenv import load_dotenv

# for convenient debug, has no effect in production
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

import supervisely as sly
from supervisely.app.widgets import Container

import src.globals as g

import src.ui.files as f

import src.ui.dataset_info as dataset_info
import src.ui.select_videos as select_videos
import src.ui.left_video as left_video
import src.ui.right_video as right_video
import src.ui.tagging as tagging
import src.ui.attributes as attrs
import src.ui.team_files as team_files


input_cards = Container(
    widgets=[left_video.card, right_video.card], direction="horizontal", gap=15, fractions=[1, 1]
)

info_cards = Container(
    widgets=[dataset_info.card, team_files.card], direction="horizontal", gap=15, fractions=[1, 1]
)


layout = Container(
    widgets=[info_cards, select_videos.card, input_cards, tagging.layout, attrs.card],
    direction="vertical",
    gap=15,
)


app = sly.Application(layout=layout)
