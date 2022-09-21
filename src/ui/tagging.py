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
from supervisely.video_annotation.video_tag import VideoTag

PREFIX_BEGIN = "begin-"
PREFIX_END = "end-"

STATUS_IN_PROGRESS = "⏳ In progress"
STATUS_DONE = "✅ Done"

show_segments_btn = Button("Show all segments", icon="zmdi zmdi-eye")
show_segments_btn.disable()

close_pair_btn = Button("Select other videos", icon="zmdi zmdi-rotate-left")
close_pair_btn.hide()

mark_segment_btn = Button("Create segment", icon="zmdi zmdi-label")
mark_segment_btn.hide()

start_tagging_btn = Button("Start segments tagging", icon="zmdi zmdi-play")
start_tagging_btn.hide()

done_tagging_btn = Button("Mark videos as done", icon="zmdi zmdi-check-all", button_type="success")
done_tagging_btn.hide()

help_text = Text(
    "Please, finish previous steps to preview existing tags and start tagging", status="warning"
)
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
    "4️⃣ Assigned tags",
    "Create, preview, navigate and manage tagged segments",
    content=Container([table]),
    slot_content=Flexbox(
        [done_tagging_btn, close_pair_btn],
    ),
    lock_message='Press 👆 "Show segments" button to create and manage segments',
)
card.lock()

layout = Container(
    widgets=[
        Flexbox(
            [show_segments_btn, start_tagging_btn, mark_segment_btn],
            center_content=True,
            gap=0,
        ),
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


@show_segments_btn.click
def show_segments_ui():
    table.loading = True
    try:
        # _start_tagging()
        _show_segments()
        select_videos.card.lock(message=select_videos.LABELING_LOCK_MESSAGE)
        select_videos.card.collapse()
        select_videos.reselect_pair_btn.show()
        card.unlock()
        show_segments_btn.hide()
        start_tagging_btn.show()
        # mark_segment_btn.show()
        # input_dataset.card.collapse()
        # select_tag.card.collapse()
    except Exception as e:
        raise e
    finally:
        table.loading = False


def _show_segments():
    global pairs
    from src.ui.select_tag import get_tag_meta

    working_tag_meta = get_tag_meta()
    left_id = left_video.player.video_id
    right_id = right_video.player.video_id
    left_tags = g.api.video.tag.get_list(left_id, g.project_meta)
    right_tags = g.api.video.tag.get_list(right_id, g.project_meta)
    pairs = defaultdict(lambda: {"begin_tag": None, "end_tag": None})

    def _process_segment_tags(video_tags: sly.VideoTagCollection, pair_key, prefix):
        for t in video_tags:
            if t.name == working_tag_meta.name and t.value.startswith(prefix):
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

    _process_segment_tags(left_tags, "begin_tag", PREFIX_BEGIN)
    _process_segment_tags(right_tags, "end_tag", PREFIX_END)
    _build_df()

    select_videos.set_video_status(left_id, left_tags, STATUS_IN_PROGRESS)
    if left_id != right_id:
        select_videos.set_video_status(right_id, right_tags, STATUS_IN_PROGRESS)
    select_videos.table.clear_selection()


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
        if mark_segment_btn.is_hidden():
            raise DialogWindowError(
                "Delete action is not allowed in preview mode",
                'Press start "Start tagging" button to create and remove segments',
            )
            return

        table.loading = True
        try:

            def _delete(tag: VideoTag):
                if tag is not None:
                    g.api.video.tag.remove(tag)

            _delete(pairs[segment_id]["begin_tag"])
            _delete(pairs[segment_id]["end_tag"])
            pairs.pop(segment_id)
            table.delete_row(COL_ID, segment_id)
        except Exception as e:
            raise e
        finally:
            table.loading = False

    table.clear_selection()


def get_new_segment_id() -> int:
    if len(pairs.keys()) == 0:
        return 1
    return max(list(pairs.keys())) + 1


@mark_segment_btn.click
def create_segment():
    table.loading = True
    try:
        segment_id = get_new_segment_id()
        tag_meta = select_tag.get_tag_meta()

        left_frame = left_video.player.get_current_frame()
        left_value = f"{PREFIX_BEGIN}{segment_id}"
        right_frame = right_video.player.get_current_frame()
        right_value = f"{PREFIX_END}{segment_id}"

        left_tag = sly.VideoTag(tag_meta, left_value, [left_frame, left_frame])
        g.api.video.tag.add(left_video.player.video_id, left_tag)

        right_tag = sly.VideoTag(tag_meta, right_value, [right_frame, right_frame])
        g.api.video.tag.add(right_video.player.video_id, right_tag)

        pairs[segment_id]["begin_tag"] = left_tag
        pairs[segment_id]["end_tag"] = right_tag
        row = _create_row(segment_id, left_tag, right_tag)
        table.insert_row(row)
    except Exception as e:
        raise e
    finally:
        table.loading = False


@start_tagging_btn.click
def start_tagging_ui():
    start_tagging_btn.hide()
    mark_segment_btn.show()
    done_tagging_btn.show()
    close_pair_btn.show()
    select_videos.card.lock(message=select_videos.LABELING_LOCK_MESSAGE)
    select_videos.card.collapse()


def _close_video_pair():
    card.lock()
    close_pair_btn.hide()
    mark_segment_btn.hide()
    done_tagging_btn.hide()
    start_tagging_btn.hide()
    show_segments_btn.show()
    show_segments_btn.disable()
    help_text.show()
    left_video.card.lock()
    right_video.card.lock()
    select_videos.card.uncollapse()
    select_videos.card.unlock()


@close_pair_btn.click
def close_video_pair():
    _close_video_pair()


@done_tagging_btn.click
def mark_videos_as_done():
    left_id = left_video.player.video_id
    right_id = right_video.player.video_id
    left_tags = g.api.video.tag.get_list(left_id, g.project_meta)
    select_videos.set_video_status(left_id, left_tags, STATUS_DONE, update=True)
    if left_id != right_id:
        right_tags = g.api.video.tag.get_list(right_id, g.project_meta)
        select_videos.set_video_status(right_id, right_tags, STATUS_DONE, update=True)
    _close_video_pair()
