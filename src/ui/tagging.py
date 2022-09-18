from collections import defaultdict
from typing import Dict, List
import pandas as pd
import supervisely as sly
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.widgets import Card, Container, Button, Flexbox, Container, Text, Table

import src.globals as g
import src.ui.input_dataset as input_dataset
import src.ui.select_tag as select_tag
import src.ui.select_videos as select_videos
import src.ui.left_video as left_video
import src.ui.right_video as right_video

PREFIX_BEGIN = "begin-"
PREFIX_END = "end-"

start_tagging_btn = Button("Start tagging", icon="zmdi zmdi-play")
start_tagging_btn.disable()

mark_segment_btn = Button("Create segment", icon="zmdi zmdi-label")
mark_segment_btn.hide()

help_text = Text("Please, finish previous steps to start tagging", status="warning")
help_block = Flexbox([help_text], center_content=True)

columns = ["Segment ID", "begin", "end", "preview", "delete"]
pairs = None
lines = None
df = None
table = Table(fixed_cols=1)


card = Card(
    "Assigned tags",
    "Create, preview, navigate and manage tagged segments",
    content=Container([table]),
    lock_message='Press 👆 "START TAGGING" button to create and manage segments',
)
card.lock()

layout = Container(
    widgets=[
        Flexbox([start_tagging_btn, mark_segment_btn], center_content=True, gap=0),
        help_block,
        card,
    ],
    gap=15,
)


def _get_frame_from_value(tag: sly.Tag) -> int:
    value = tag.value
    prefix = None
    if value.startswith(PREFIX_BEGIN):
        prefix = PREFIX_BEGIN
    elif value.startswith(PREFIX_END):
        prefix = PREFIX_END
    else:
        raise ValueError(
            f"Can not parse Segment ID from tag {value}. Make sure you selected correct tag on step 2"
        )
    frame_index = None
    frame_str = value.lstrip(prefix)
    if frame_str.isdigit():
        frame_index = int(frame_str)
    if frame_index is None:
        raise ValueError("Can not parse Segment ID from string {value}")
    return frame_index


def _build_df():
    global lines, df
    lines = []
    for segment_id, d in pairs.items():
        lines.append(
            [
                segment_id,
                d["begin_tag"].frame_range[0],
                d["end_tag"].frame_range[0],
                sly.app.widgets.Table.create_button("preview"),
                sly.app.widgets.Table.create_button("delete"),
            ]
        )

    df = pd.DataFrame(lines, columns=columns)
    table.read_pandas(df)


@start_tagging_btn.click
def start_tagging_ui():
    table.loading = True
    try:
        _start_tagging()
        select_videos.card.collapse()
        card.unlock()
        mark_segment_btn.show()
        start_tagging_btn.hide()
        input_dataset.card.collapse = True
        select_tag.card.collapse = True
    except Exception as e:
        raise e
    finally:
        table.loading = False


def _start_tagging():
    global pairs
    from src.ui.select_tag import get_tag_meta

    working_tag_meta = get_tag_meta()

    left_id = 3267369  # TODO: left_video.player.video_id
    right_id = 3267370  # TODO: right_video.player.video_id

    left_ann_json = g.api.video.annotation.download(left_id)
    left_key_id_map = sly.KeyIdMap()
    left_ann = sly.VideoAnnotation.from_json(left_ann_json, g.project_meta, left_key_id_map)

    right_ann_json = g.api.video.annotation.download(right_id)
    right_key_id_map = sly.KeyIdMap()
    right_ann = sly.VideoAnnotation.from_json(right_ann_json, g.project_meta, right_key_id_map)

    pairs = defaultdict(lambda: {"begin_tag": None, "end_tag": None})

    def _process_segment_tags(video_tags, pair_key):
        for t in video_tags:
            if t.name == working_tag_meta.name:
                if t.frame_range is None:
                    raise ValueError(
                        "Tag does not assigned to any frame. Make sure you selected correct tag on step 2"
                    )
                if t.frame_range[0] != t.frame_range[1]:
                    raise ValueError(
                        "Frame range has to contain only one frame. Make sure you selected correct tag on step 2"
                    )
                segment_id = _get_frame_from_value(t)
                pairs[segment_id][pair_key] = t

    _process_segment_tags(left_ann.tags, "begin_tag")
    _process_segment_tags(right_ann.tags, "end_tag")
    _build_df()


@table.click
def handle_table_button(datapoint: sly.app.widgets.Table.ClickedDataPoint):
    if datapoint.button_name is None:
        return
    segment_id = datapoint.row["Segment ID"]
    begin_frame = datapoint.row["begin"]
    end_frame = datapoint.row["end"]

    if datapoint.button_name == "preview":
        left_video.player.set_current_frame(begin_frame)
        right_video.player.set_current_frame(end_frame)
    elif datapoint.button_name == "delete":
        raise NotImplementedError()
