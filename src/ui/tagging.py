import supervisely as sly
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.widgets import (
    Card,
    Container,
    Button,
    Flexbox,
    Container,
    Text,
)

import src.globals as g
import src.ui.select_videos as select_videos
import src.ui.left_video as left_video
import src.ui.right_video as right_video


start_tagging_btn = Button("Start tagging", icon="zmdi zmdi-play")
mark_segment_btn = Button("Create segment", icon="zmdi zmdi-label")
mark_segment_btn.hide()

help_text = Text("Please, finish previous steps to start tagging", status="warning")
help_block = Flexbox([help_text], center_content=True)
start_tagging_btn.disable()

# segments management


card = Card(
    "Assigned tags",
    "Create, preview, navigate and manage tagged segments",
    lock_message='Press 👆 "START TAGGING" button to create and manage segments',
)
# card.lock()

layout = Container(
    widgets=[
        Flexbox([start_tagging_btn, mark_segment_btn], center_content=True, gap=0),
        help_block,
        card,
    ],
    gap=15,
)


@start_tagging_btn.click
def start_tagging():
    from src.ui.select_tag import get_tag_meta

    # get all video1 tags for selected tag meta
    # get all video2 tags for selected tag meta
    # match tags, skip (remove?) all unmatched pairs
    # show table with pairs with buttons (delete, show)
    # left_video.player.video_id
    left_id = left_video.player.video_id
    right_id = right_video.player.video_id

    left_ann_json = g.api.video.annotation.download(left_id)
    left_key_id_map = sly.KeyIdMap()
    left_ann = sly.VideoAnnotation.from_json(left_ann_json, g.project_meta, left_key_id_map)

    right_ann_json = g.api.video.annotation.download(right_id)
    right_key_id_map = sly.KeyIdMap()
    right_ann = sly.VideoAnnotation.from_json(right_ann_json, g.project_meta, right_key_id_map)

    beginnings = []

    working_tag_meta = get_tag_meta()
    for t in left_ann.tags:
        if t.name == working_tag_meta.name:
            beginnings.append(t)

    endings = []
    for t in right_ann.tags:
        if t.name == working_tag_meta.name:
            endings.append(t)

    select_videos.card.collapse()
    card.unlock()
    mark_segment_btn.show()
    start_tagging_btn.hide()
