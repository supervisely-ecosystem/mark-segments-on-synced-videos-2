import os
from dotenv import load_dotenv
import supervisely as sly
from supervisely.app.widgets import (
    Card,
    Container,
    Video,
    DatasetThumbnail,
    ProjectThumbnail,
)

# for convenient debug, has no effect in production
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))
api = sly.Api()

# @TODO:
# reimplement project / dataset envs on agent + documentation
# Dataset Thumbnail
# Select tag
# emoji as step number 1️⃣  - https://www.npmjs.com/package/number-to-emoji

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

dataset_id = int(os.environ["context.datasetId"])
dataset_info = api.dataset.get_info_by_id(dataset_id, raise_error=True)
project_info = api.project.get_info_by_id(dataset_info.project_id)

input_dataset = Card(
    "Input dataset",
    "Label video or pair of videos in current dataset",
    content=DatasetThumbnail(project_info, dataset_info),
)
input_tag = Card(
    "Select Tag",
    "Select key-value(str) tag for labeling",
    content=ProjectThumbnail(project_info),
)

settings = Container(
    [input_dataset, input_tag], direction="horizontal", gap=15, fractions=[1, 1]
)

vid1 = 3267369
vid2 = 3267370
v1 = Video(vid1)
v2 = Video(vid2)
card1 = Card("Input video #1", "Select first video", content=v1)
card2 = Card("Input video #2", "Select second video", content=v2)

input_cards = Container(
    widgets=[card1, card2], direction="horizontal", gap=15, fractions=[1, 1]
)

card = Card("Tagging", "Description")
layout = Container(widgets=[settings, input_cards, card], direction="vertical", gap=15)


app = sly.Application(layout=layout)

# from starlette.responses import FileResponse
# @app.get('/favicon.ico')
# def favicon():
#     return FileResponse(os.path.join(app_root_directory, 'static', 'favicon.png'))
