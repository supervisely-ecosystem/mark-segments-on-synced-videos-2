import supervisely as sly
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.fastapi.request import Request
from supervisely.app.widgets import (
    Card,
    Container,
    Button,
    Flexbox,
    Container,
    Text,
)

import src.globals as g
import src.ui.left_video as left_video
import src.ui.right_video as right_video
import src.ui.select_videos as select_videos


start_tagging_btn = Button("Start tagging", icon="zmdi zmdi-play")
help_text = Text("Please, finish previous steps to start tagging", status="warning")
help_block = Flexbox([help_text], center_content=True)
start_tagging_btn.disable()

card = Card(
    "Assigned tags",
    "Create, preview, navigate and manage tagged segments",
    lock_message='Press 👆 "START TAGGING" button to create and manage segments',
)
card.lock()

layout = Container(
    widgets=[
        Flexbox([start_tagging_btn], center_content=True),
        help_block,
        card,
    ],
    gap=15,
)


@start_tagging_btn.click
def start_tagging(request: Request):
    # get user api object
    # get all video1 tags for selected tag meta
    # get all video2 tags for selected tag meta
    # match tags, skip (remove?) all unmatched pairs
    # show table with pairs with buttons (delete, show)
    pass
    # select_videos.card.collapse()
