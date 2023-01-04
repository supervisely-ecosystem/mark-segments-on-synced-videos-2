from collections import defaultdict
import datetime
from itertools import product
import pandas as pd
from typing import Dict, List

import supervisely as sly
from supervisely.annotation.tag_meta import TagMeta, TagValueType
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.widgets import Card, Container, Button, Flexbox, Container, Text, Table

import src.globals as g
import src.ui.select_tag as select_tag
import src.ui.select_videos as select_videos
import src.ui.left_video as left_video
import src.ui.right_video as right_video
from supervisely.video_annotation.video_tag import VideoTag

PREFIX_BEGIN = "begin-"
PREFIX_END = "end-"
PREFIX_BEGIN_ATTRS = "begin_attrs-"
PREFIX_END_ATTRS = "end_attrs-"

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
COL_BEGIN = "Begin (left)".upper()
COL_END = "End (right)".upper()
COL_ATTRS = "Attributes".upper()
COL_PREVIEW = "Preview".upper()
COL_EDIT = "Edit".upper()
COL_DELETE = "Delete".upper()

columns = [
    COL_ID,
    COL_USER,
    COL_DT,
    COL_BEGIN,
    COL_END,
    COL_ATTRS,
    COL_PREVIEW,
    COL_EDIT,
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
    content_top_right=Flexbox(
        [done_tagging_btn, close_pair_btn],
    ),
    lock_message='Press 👆 "Show segments" button to create and manage segments',
)
card.lock()

layout = Container(
    widgets=[
        Flexbox(
            [
                show_segments_btn,
                start_tagging_btn,
                mark_segment_btn,
            ],
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
    attrs_tag = None
    if value.startswith(PREFIX_BEGIN):
        prefix = PREFIX_BEGIN
    elif value.startswith(PREFIX_END):
        prefix = PREFIX_END
    elif value.startswith(PREFIX_END_ATTRS):
        prefix = PREFIX_END_ATTRS
    elif value.startswith(PREFIX_BEGIN_ATTRS):
        prefix = PREFIX_BEGIN_ATTRS
    else:
        raise ValueError(
            f"Can not parse Segment ID from tag {value}. Make sure you selected correct tag on step 2"
        )
    # frame_index = None
    frame_str = value.lstrip(prefix)
    if prefix == PREFIX_END_ATTRS or prefix == PREFIX_BEGIN_ATTRS:
        attrs_tag = frame_str.split("-")[-1]
        frame_str = frame_str.split("-")[0]
    # if frame_str.isdigit():
    #     frame_index = int(frame_str)
    # if frame_index is None:
    #     raise ValueError(f"Can not parse Segment ID from string {value}")
    return frame_str, attrs_tag


def _create_row(
    segment_id: str, begin: VideoTag, end: VideoTag, left_attr: VideoTag, right_attr: VideoTag
):
    dt = None
    user = None
    attrs = []

    if begin is not None:
        dt = sly.get_readable_datetime(begin.created_at)
        user = begin.labeler_login
        left_video_frames_to_timecodes = g.choosed_videos["left_video"].frames_to_timecodes
        begin_timestamp_seconds = round(left_video_frames_to_timecodes[begin.frame_range[0]], 1)
        begin_timestamp = get_readable_timestamp(begin_timestamp_seconds)

    if end is not None:
        dt = sly.get_readable_datetime(end.created_at)
        user = end.labeler_login
        right_video_frames_to_timecodes = g.choosed_videos["right_video"].frames_to_timecodes
        end_timestamp_seconds = round(right_video_frames_to_timecodes[end.frame_range[0]], 1)
        end_timestamp = get_readable_timestamp(end_timestamp_seconds)

    if left_attr is not None:
        attrs.append(_get_frame_from_value(left_attr)[1])
    if right_attr is not None:
        attrs.append(_get_frame_from_value(right_attr)[1])

    row = [
        segment_id,
        user,
        dt,
        begin_timestamp if begin is not None else None,
        end_timestamp if end is not None else None,
        "".join(
            [
                f"<span style='padding: 4px; margin: 3px;background-color: lemonchiffon;'>{attr}</span>"
                for attr in attrs
            ]
        )
        if len(attrs) > 0
        else None,
        sly.app.widgets.Table.create_button(COL_PREVIEW),
        sly.app.widgets.Table.create_button("SET"),
        sly.app.widgets.Table.create_button(COL_DELETE),
    ]
    return row


def _build_df():
    global lines, df
    lines = []
    for segment_id, d in pairs.items():
        lines.append(
            _create_row(segment_id, d["begin_tag"], d["end_tag"], d["begin_attrs"], d["end_attrs"])
        )
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
    left_id = g.choosed_videos["left_video"].id
    right_id = g.choosed_videos["right_video"].id
    left_tags = g.api.video.tag.download_list(left_id, g.project_meta)
    right_tags = g.api.video.tag.download_list(right_id, g.project_meta)
    pairs = defaultdict(
        lambda: {"begin_tag": None, "end_tag": None, "begin_attrs": None, "end_attrs": None}
    )
    g.all_segments = defaultdict(dict)

    # tags_grid = product(left_tags, right_tags)
    # for l, r in tags_grid:
    #     if l.name != working_tag_meta.name or r.name != working_tag_meta.name:
    #         continue
    #     if l.value.startswith(PREFIX_BEGIN) and r.value.startswith(PREFIX_END):
    #         if l.frame_range is None or r.frame_range is None:
    #             raise ValueError(
    #                 "Tag does not assigned to any frame. Make sure you selected correct tag on step 2"
    #             )
    #         if l.frame_range[0] != l.frame_range[1] or r.frame_range[0] != r.frame_range[1]:
    #             raise ValueError(
    #                 "Frame range has to contain only one frame. Make sure you selected correct tag on step 2"
    #             )
    #         segment_id_l = _get_frame_from_value(l)
    #         segment_id_r = _get_frame_from_value(r)
    #         if segment_id_l != segment_id_r:
    #             continue
    #         segment_id = segment_id_l
    #         pairs[segment_id]["begin_tag"] = l
    #         pairs[segment_id]["end_tag"] = r

    def _process_segment_tags(video_tags: sly.VideoTagCollection, pair_key, prefix):
        for t in video_tags:
            if t.value.startswith(prefix):
                if t.frame_range is None:
                    raise ValueError(
                        "Tag does not assigned to any frame. Make sure you selected correct tag on step 2"
                    )
                if t.frame_range[0] != t.frame_range[1]:
                    raise ValueError(
                        "Frame range has to contain only one frame. Make sure you selected correct tag on step 2"
                    )
                if t.name == working_tag_meta.name or prefix in [
                    PREFIX_BEGIN_ATTRS,
                    PREFIX_END_ATTRS,
                ]:
                    segment_id, attrs_tag = _get_frame_from_value(t)
                    if attrs_tag is not None:
                        g.all_segments[segment_id][pair_key] = attrs_tag
                    pairs[segment_id][pair_key] = t

    _process_segment_tags(left_tags, "begin_tag", PREFIX_BEGIN)
    _process_segment_tags(left_tags, "begin_attrs", PREFIX_BEGIN_ATTRS)
    _process_segment_tags(right_tags, "end_tag", PREFIX_END)
    _process_segment_tags(right_tags, "end_attrs", PREFIX_END_ATTRS)
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
            begin_timestamp = get_timestamp_from_str(begin_frame)
            left_video.player.set_current_timestamp(begin_timestamp)
        else:
            raise DialogWindowError(
                "Incorrect segment",
                "Begin Frame is not defined on left video. Make sure you selected correct pair of videos.",
            )
        if end_frame is not None:
            end_timestamp = get_timestamp_from_str(end_frame)
            right_video.player.set_current_timestamp(end_timestamp)
        else:
            raise DialogWindowError(
                "Incorrect segment",
                "End Frame is not defined on right video. Make sure you selected correct pair of videos.",
            )
    elif datapoint.button_name == COL_EDIT:
        if mark_segment_btn.is_hidden():
            raise DialogWindowError(
                "Delete action is not allowed in preview mode",
                'Press start "Start tagging" button to create and remove segments',
            )
            return

        table.loading = True
        try:
            left_frame = get_frame_to_timestamp(left_video.player, "left_video")
            right_frame = get_frame_to_timestamp(right_video.player, "right_video")

            left_tag: VideoTag = pairs[segment_id]["begin_tag"]
            right_tag = pairs[segment_id]["end_tag"]

            g.api.video.tag.update_frame_range(left_tag.sly_id, [left_frame, left_frame])
            g.api.video.tag.update_frame_range(right_tag.sly_id, [right_frame, right_frame])

            pairs[segment_id]["begin_tag"] = left_tag
            pairs[segment_id]["end_tag"] = right_tag

            # left_video_frames_to_timecodes = g.choosed_videos["left_video"].frames_to_timecodes
            # begin_timestamp_seconds = round(left_video_frames_to_timecodes[left_frame], 1)
            # begin_timestamp = get_readable_timestamp(begin_timestamp_seconds)
            # right_video_frames_to_timecodes = g.choosed_videos["right_video"].frames_to_timecodes
            # end_timestamp_seconds = round(right_video_frames_to_timecodes[right_frame], 1)
            # end_timestamp = get_readable_timestamp(end_timestamp_seconds)

            table.update_cell_value(COL_ID, segment_id, COL_BEGIN, left_frame)
            table.update_cell_value(COL_ID, segment_id, COL_END, right_frame)
        except Exception as e:
            raise e
        finally:
            table.loading = False

        table.clear_selection()

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
            _delete(pairs[segment_id]["begin_attrs"])
            _delete(pairs[segment_id]["end_attrs"])
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
    return max(list(map(int, pairs.keys()))) + 1


@mark_segment_btn.click
def create_segment():
    table.loading = True
    try:
        segment_id = get_new_segment_id()
        left_is_broken = left_video.check_is_broken_tag.is_checked()
        right_is_broken = right_video.check_is_broken_tag.is_checked()

        left_tag, right_tag, left_attr, right_attr = create_any_segment(
            segment_id, left_is_broken, right_is_broken
        )

        row = _create_row(segment_id, left_tag, right_tag, left_attr, right_attr)
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
    select_videos.reselect_pair_btn.hide()
    select_videos.card.uncollapse()
    select_videos.card.unlock()


@close_pair_btn.click
def close_video_pair():
    _close_video_pair()


@done_tagging_btn.click
def mark_videos_as_done():
    left_id = g.choosed_videos["left_video"].id
    right_id = g.choosed_videos["right_video"].id
    left_tags = g.api.video.tag.download_list(left_id, g.project_meta)
    select_videos.set_video_status(left_id, left_tags, STATUS_DONE, update=True)
    if left_id != right_id:
        right_tags = g.api.video.tag.download_list(right_id, g.project_meta)
        select_videos.set_video_status(right_id, right_tags, STATUS_DONE, update=True)
    _close_video_pair()
    select_videos.reselect_pair_btn.show()


def get_frame_to_timestamp(player, video):
    current_timestamp = player.get_current_timestamp()
    frames_to_timecodes = g.choosed_videos[video].frames_to_timecodes
    left, right = 0, len(frames_to_timecodes) - 1
    while left < right:
        middle = (left + right) // 2
        if frames_to_timecodes[middle] == current_timestamp:
            return middle
        if frames_to_timecodes[middle] > current_timestamp:
            right = middle - 1
        elif frames_to_timecodes[middle] < current_timestamp:
            left = middle + 1
    return middle


def get_readable_timestamp(total_seconds):
    # hours = total_seconds // 3600
    # minutes = (total_seconds - hours * 3600) // 60
    # seconds = total_seconds - hours * 3600 - minutes * 60
    # return f'{hours}:{minutes}:{seconds}'
    timestamp = str(datetime.timedelta(seconds=total_seconds))
    timestamp_div = timestamp.split(".")
    if len(timestamp_div) == 1:
        return timestamp
    return timestamp[:-5]


def get_timestamp_from_str(str):
    hms = str.split(":")
    total_seconds = int(hms[0]) * 3600 + int(hms[1]) * 60 + float(hms[2])
    return total_seconds


def create_any_segment(segment_id, left=False, right=False):
    tag_meta = select_tag.get_tag_meta()
    attrs_tag_meta = select_tag.get_attrs_tag_meta()
    left_attr, right_attr = None, None

    left_frame = get_frame_to_timestamp(left_video.player, "left_video")
    right_frame = get_frame_to_timestamp(right_video.player, "right_video")

    left_value = f"{PREFIX_BEGIN}{segment_id}"
    right_value = f"{PREFIX_END}{segment_id}"

    left_tag = VideoTag(tag_meta, left_value, [left_frame, left_frame])
    right_tag = VideoTag(tag_meta, right_value, [right_frame, right_frame])

    g.api.video.tag.add(g.choosed_videos["left_video"].id, left_tag)
    g.api.video.tag.add(g.choosed_videos["right_video"].id, right_tag)

    pairs[segment_id]["begin_tag"] = left_tag
    pairs[segment_id]["end_tag"] = right_tag

    if left is True:
        left_value = f"{PREFIX_BEGIN_ATTRS}{segment_id}-begin_exit"
        left_attr = VideoTag(attrs_tag_meta, left_value, [left_frame, left_frame])
        g.api.video.tag.add(g.choosed_videos["left_video"].id, left_attr)

    if right is True:
        right_value = f"{PREFIX_END_ATTRS}{segment_id}-end_enter"
        right_attr = VideoTag(attrs_tag_meta, right_value, [right_frame, right_frame])
        g.api.video.tag.add(g.choosed_videos["right_video"].id, right_attr)

    pairs[segment_id]["begin_attrs"] = left_attr
    pairs[segment_id]["end_attrs"] = right_attr

    return left_tag, right_tag, left_attr, right_attr
