from collections import defaultdict
from typing import Dict, List
import pandas as pd
from datetime import datetime

import supervisely as sly
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.widgets import Card, Container, Button, Flexbox, Container, Text, Table

import src.globals as g
import src.ui.input_dataset as input_dataset
import src.ui.select_tag as select_tag
import src.ui.select_videos as select_videos
import src.ui.left_video as left_video
import src.ui.right_video as right_video
from supervisely.video_annotation.video_tag import VideoTag

PREFIX_BEGIN = "begin-"
PREFIX_END = "end-"

start_tagging_btn = Button("Start tagging", icon="zmdi zmdi-play")
# start_tagging_btn.disable()

mark_segment_btn = Button("Create segment", icon="zmdi zmdi-label")
mark_segment_btn.hide()

help_text = Text("Please, finish previous steps to start tagging", status="warning")
help_block = Flexbox([help_text], center_content=True)

COL_ID = "Segment ID".upper()
COL_USER = "User".upper()
COL_DT = "Created at".upper()
COL_BEGIN = "Begin Frame (left)".upper()
COL_END = "End Frame (right)".upper()
COL_PREVIEW = "Preview".upper()
COL_DELETE = "Delete".upper()

columns = [
    COL_ID,
    COL_USER,
    COL_DT,
    COL_BEGIN,
    COL_END,
    COL_PREVIEW,
    COL_DELETE,
]
pairs: Dict = None
lines: List = None
df: pd.DataFrame = None
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


def _create_row(segment_id: str, begin: VideoTag, end: VideoTag):
    dt = None
    user = None

    if begin is not None:
        dt = sly.get_readable_datetime(begin.created_at)
        user = begin.labeler_login
    elif end is not None:
        dt = sly.get_readable_datetime(end.created_at)
        user = end.labeler_login

    row = [
        segment_id,
        user,
        dt,
        begin.frame_range[0] if begin is not None else None,
        end.frame_range[0] if end is not None else None,
        sly.app.widgets.Table.create_button(COL_PREVIEW),
        sly.app.widgets.Table.create_button(COL_DELETE),
    ]
    return row


def _build_df():
    global lines, df
    lines = []
    for segment_id, d in pairs.items():
        lines.append(_create_row(segment_id, d["begin_tag"], d["end_tag"]))
    df = pd.DataFrame(lines, columns=columns)
    table.read_pandas(df)


@start_tagging_btn.click
def start_tagging_ui():
    table.loading = True
    try:
        _start_tagging()
        select_videos.card.lock(message=select_videos.LABELING_LOCK_MESSAGE)
        select_videos.card.collapse()
        card.unlock()
        mark_segment_btn.show()
        start_tagging_btn.hide()
        input_dataset.card.collapse()
        select_tag.card.collapse()
    except Exception as e:
        raise e
    finally:
        table.loading = False


def _start_tagging():
    global pairs
    from src.ui.select_tag import get_tag_meta

    working_tag_meta = get_tag_meta()

    left_id = left_video.player.video_id
    right_id = right_video.player.video_id

    left_tags = g.api.video.tag.get_list(left_id, g.project_meta)
    right_tags = g.api.video.tag.get_list(right_id, g.project_meta)

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

    _process_segment_tags(left_tags, "begin_tag")
    _process_segment_tags(right_tags, "end_tag")
    _build_df()


@table.click
def handle_table_button(datapoint: sly.app.widgets.Table.ClickedDataPoint):
    if datapoint.button_name is None:
        return
    segment_id = datapoint.row[COL_ID]
    begin_frame = datapoint.row[COL_BEGIN]
    end_frame = datapoint.row[COL_END]

    if datapoint.button_name == COL_PREVIEW:
        if begin_frame is not None:
            left_video.player.set_current_frame(begin_frame)
        else:
            raise DialogWindowError(
                "Incorrect segment",
                "Begin Frame is not defined on left video. Make sure you selected correct pair of videos.",
            )
        if end_frame is not None:
            right_video.player.set_current_frame(end_frame)
        else:
            raise DialogWindowError(
                "Incorrect segment",
                "End Frame is not defined on right video. Make sure you selected correct pair of videos.",
            )
    elif datapoint.button_name == COL_DELETE:
        # http://78.46.75.100:38589/#tag/Videos/paths/~1videos.tags.remove/delete
        raise NotImplementedError()


def reset():
    mark_segment_btn.hide()
    start_tagging_btn.show()
    select_tag.card.collapse()
    select_tag.card.lock()


def get_new_segment_id() -> int:
    return max(list(pairs.keys())) + 1


@mark_segment_btn.click
def create_segment():
    segment_id = get_new_segment_id()
    tag_meta = select_tag.get_tag_meta()

    left_frame = left_video.player.get_current_frame()
    left_value = f"{PREFIX_BEGIN}{segment_id}"
    right_frame = right_video.player.get_current_frame()
    right_value = f"{PREFIX_END}{segment_id}"

    # @TODO: how to get UserId, CreatedAt, UpdatedAt
    # created_at=datatime.now()
    # updated_at

    left_tag = sly.VideoTag(
        tag_meta,
        left_value,
        [left_frame, left_frame],
        labeler_login=g.user.login,
        created_at=None,
        updated_at=None,
    )
    # @TODO: update labeler and timestamps
    g.api.video.tag.add(left_video.player.video_id, left_tag)

    right_tag = sly.VideoTag(
        tag_meta,
        right_value,
        [right_frame, right_frame],
        labeler_login=g.user.login,
        created_at=None,
        updated_at=None,
    )
    g.api.video.tag.add(right_video.player.video_id, right_tag)

    pairs[segment_id]["begin_tag"] = left_tag
    pairs[segment_id]["end_tag"] = right_tag
    row = _create_row(segment_id, left_tag, right_tag)
    table.add_row(row)
