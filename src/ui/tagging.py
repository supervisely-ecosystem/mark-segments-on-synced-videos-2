from bs4 import BeautifulSoup
import datetime
import io
import json
import os
import pandas as pd
from typing import List

import supervisely as sly
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.widgets import Card, Container, Button, Flexbox, Container, Text, Table

import src.globals as g
import src.ui.files as f
import src.ui.left_video as left_video
import src.ui.right_video as right_video
import src.ui.select_videos as select_videos
import src.ui.attributes as attrs


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
COL_UPDATED_AT = "Updated at".upper()
COL_BEGIN = "Begin (left)".upper()
COL_END = "End (right)".upper()
COL_ATTRIBUTES = "Attributes".upper()
COL_EDIT = "Edit attributes".upper()
COL_PREVIEW = "Preview".upper()
COL_DELETE = "Delete".upper()

EDIT_BTN = f"EDIT <i class='zmdi zmdi-edit'>"

columns = [
    COL_ID,
    COL_USER,
    COL_UPDATED_AT,
    COL_BEGIN,
    COL_END,
    COL_ATTRIBUTES,
    COL_EDIT,
    COL_PREVIEW,
    COL_DELETE,
]

lines: List = None
df: pd.DataFrame = None
table = Table()

card = Card(
    "3️⃣ Assigned tags",
    "Create, preview, navigate and manage tagged segments",
    content=Container([table]),
    content_top_right=Flexbox(
        [done_tagging_btn, close_pair_btn],
    ),
    lock_message='Press 👆 "Show segments" button to create and manage segments',
)
card.hide()

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


@show_segments_btn.click
def show_segments_ui():
    table.loading = True
    try:
        card.unlock()
        _show_segments()
        select_videos.card.lock(message=select_videos.LABELING_LOCK_MESSAGE)
        select_videos.card.collapse()
        select_videos.reselect_pair_btn.show()
        card.show()
        show_segments_btn.hide()
        start_tagging_btn.show()
    except Exception as e:
        raise e
    finally:
        table.loading = False


@mark_segment_btn.click
def create_segment():
    table.loading = True

    try:
        custom_data = g.api.project.get_info_by_id(g.project_id).custom_data
        unchecked_segment_id = None
        if "segment_id" in custom_data.keys():
            unchecked_segment_id = int(custom_data["segment_id"])

        segment_id = _check_new_segment_id(unchecked_segment_id)
        if segment_id is None:
            raise DialogWindowError(
                "Incorrect segment id",
                "Segment_id is None. Check that number 'segment_id' exists in project custom_data.",
            )

        new_segment_file = os.path.join(select_videos.pairs_dir_name, f"segment-{segment_id}.json")

        left_timestamp = left_video.player.get_current_timestamp()
        right_timestamp = right_video.player.get_current_timestamp()
        timestamps = {
            "left": left_timestamp,
            "right": right_timestamp,
        }
        updated_at = datetime.datetime.now().strftime("%d %B %Y  %H:%M:%S")
        created_at = datetime.datetime.now().strftime("%d %B %Y  %H:%M:%S")
        user_name = g.user_info.login

        data = {
            "left_video": {
                "id": g.choosed_videos["left_video"].id,
                "name": g.choosed_videos["left_video"].name,
                "timestamp": left_timestamp,
            },
            "right_video": {
                "id": g.choosed_videos["right_video"].id,
                "name": g.choosed_videos["right_video"].name,
                "timestamp": right_timestamp,
            },
            "tags": [],
            "created_at": created_at,
            "updated_at": updated_at,
            "user_name": user_name,
        }

        with io.open(new_segment_file, "w", encoding="utf-8") as file:
            str_ = json.dumps(
                data, indent=4, separators=(",", ": "), ensure_ascii=False
            )
            file.write(str(str_))

        g.api.file.upload(g.team_id, new_segment_file, new_segment_file)
        tags = sly.TagCollection()
        row = _create_row(segment_id, new_segment_file, timestamps, user_name, updated_at, tags)
        table.insert_row(data=row)

    except Exception as e:
        raise e
    finally:
        table.loading = False


@start_tagging_btn.click
def start_tagging_ui():
    card.unlock()
    start_tagging_btn.hide()
    mark_segment_btn.show()
    done_tagging_btn.show()
    close_pair_btn.show()
    select_videos.card.lock(message=select_videos.LABELING_LOCK_MESSAGE)
    select_videos.card.collapse()


@close_pair_btn.click
def close_video_pair():
    _close_video_pair()


@table.click
def handle_table_button(datapoint: sly.app.widgets.Table.ClickedDataPoint):
    if datapoint.button_name is None:
        return
    segment_id = datapoint.row[COL_ID]
    begin_frame = datapoint.row[COL_BEGIN]
    end_frame = datapoint.row[COL_END]

    if datapoint.button_name == COL_PREVIEW:
        if begin_frame is not None:
            begin_timestamp = _get_timestamp_from_str(begin_frame)
            left_video.player.set_current_timestamp(begin_timestamp)
        else:
            raise DialogWindowError(
                "Incorrect segment",
                "Begin Frame is not defined on left video. Make sure you selected correct pair of videos.",
            )
        if end_frame is not None:
            end_timestamp = _get_timestamp_from_str(end_frame)
            right_video.player.set_current_timestamp(end_timestamp)
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
            segment_filepath = os.path.join(
                select_videos.pairs_dir_name, f"segment-{segment_id}.json"
            )
            g.api.file.remove(g.team_id, segment_filepath)
            os.remove(segment_filepath)

            table.delete_row(COL_ID, segment_id)
        except Exception as e:
            raise e
        finally:
            table.loading = False

    elif datapoint.button_name == EDIT_BTN:
        card.lock(message="Select tags below and press 'SAVE TAGS' button")
        done_tagging_btn.hide()
        mark_segment_btn.hide()
        close_pair_btn.hide()
        start_tagging_btn.hide()
        segment_id = datapoint.row[COL_ID]
        attrs.segment_id_text.text = f"Current segment ID: <b>{segment_id}</b>"
        attrs.show_attrs_card(segment_id)
    table.clear_selection()


@table.download_as_csv
def download_segments_info_as_csv():
    left_id = g.choosed_videos["left_video"].id
    right_id = g.choosed_videos["right_video"].id
    pairs_dir_name = os.path.join(f.ds_path, f"video-pair-{left_id}-{right_id}")

    if len(g.api.file.listdir(g.team_id, pairs_dir_name)) == 0:
        empty_df = pd.DataFrame()
        return empty_df

    df = table.to_pandas()
    df.index.name = "Segments info table"

    for rowIndex, row in df.iterrows():
        for columnIndex, value in row.items():
            if value is None:
                clean_text = ""
            else:
                soup = BeautifulSoup(str(value), "html.parser")
                text = soup.get_text("", strip=True)
                text = [s.strip() for s in text.split("• ")]
                if len(text) > 1:
                    text = text[1:]
                clean_text = ", ".join(text)

            df.at[rowIndex, columnIndex] = clean_text
            new_df = df.drop([COL_EDIT, COL_PREVIEW, COL_DELETE], axis="columns")

    return new_df


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
    f.clean_local_video_pair_dir(left_id, right_id)


def _check_new_segment_id(id):
    if id is None:
        return None

    if not _check_if_segment_id_exists(id):
        g.api.project.update_custom_data(g.project_id, {"segment_id": id + 1})
        return id
    return _check_new_segment_id(id + 1)


def _check_if_segment_id_exists(id):
    all_segments = []
    ds_files = g.api.file.list2(g.team_id, f.ds_path)
    if len(ds_files) > 0:
        for file in ds_files:
            all_segments.append(file.name)
    return f"segment-{id}.json" in all_segments


def _show_segments():
    left_video_id = g.choosed_videos["left_video"].id
    right_video_id = g.choosed_videos["right_video"].id
    pairs_dir_name = os.path.join(f.ds_path, f"video-pair-{left_video_id}-{right_video_id}")

    if f"video-pair-{left_video_id}-{right_video_id}" in os.listdir(f.ds_path):
        sly.fs.remove_dir(pairs_dir_name)
    if g.api.file.dir_exists(g.team_id, pairs_dir_name):
        g.api.file.download_directory(g.team_id, pairs_dir_name, pairs_dir_name)
    if not sly.fs.dir_exists(pairs_dir_name):
        sly.fs.mkdir(pairs_dir_name)

    left_tags = g.api.video.tag.download_list(left_video_id, g.project_meta)
    right_tags = g.api.video.tag.download_list(right_video_id, g.project_meta)
    select_videos.set_video_status(left_video_id, left_tags, STATUS_IN_PROGRESS)
    if left_video_id != right_video_id:
        select_videos.set_video_status(right_video_id, right_tags, STATUS_IN_PROGRESS)
    select_videos.table.clear_selection()
    select_videos.extra_table.clear_selection()

    _build_df(pairs_dir_name)


def _build_df(pairs_dir_name):
    global lines, df
    lines = []
    if not sly.fs.dir_exists(pairs_dir_name):
        df = pd.DataFrame(lines, columns=columns)
        table.read_pandas(df)
        return
    segments_files = os.listdir(pairs_dir_name)
    if len(segments_files) > 0:
        for file in segments_files:
            tags_to_delete = []
            t_error = None
            file_path = os.path.join(pairs_dir_name, file)
            file_name = os.path.splitext(file)[0]
            with io.open(file_path) as j:
                d = json.load(j)
                segment_id = file_name.split("-")[-1]
                timestamps = {
                    "left": d["left_video"]["timestamp"],
                    "right": d["right_video"]["timestamp"],
                }
                updated_at = None
                if "updated_at" in d.keys():
                    updated_at = d["updated_at"]
                user_name = None
                if "user_name" in d.keys():
                    user_name = d["user_name"]

                for tag in d["tags"]:
                    tag_meta = g.project_meta.get_tag_meta(tag["name"])
                    if tag_meta is None:
                        tags_to_delete.append(tag)
                if len(tags_to_delete) > 0:
                    for tag in tags_to_delete:
                        d["tags"].remove(tag)
                        sly.logger.warning(
                            f'Can not load tag "{tag["name"]}". Please contact tech support.'
                        )
                    t_error = attrs.t_error_msg
                tags = sly.TagCollection.from_json(d["tags"], g.project_meta.tag_metas)

                lines.append(
                    _create_row(
                        segment_id, file_path, timestamps, user_name, updated_at, tags, t_error
                    )
                )
    df = pd.DataFrame(lines, columns=columns)
    table.read_pandas(df)
    table.sort(column_id=2, direction="desc")


def _create_row(
    segment_id: str,
    file_path,
    timestamps,
    user_name,
    updated_at,
    tags: sly.TagCollection,
    t_error=None,
):
    attrs_str = None
    left_timestamp = timestamps["left"]
    right_timestamp = timestamps["right"]

    file_info = g.api.file.get_info_by_path(g.team_id, file_path)
    if updated_at is None and file_info is not None:
        updated_at = _get_readable_datetime(file_info.created_at)

    if user_name is None and file_info.user_id == g.user_info.id:
        user_name = g.user_info.login

    if left_timestamp is not None:
        begin_timestamp = _get_readable_timestamp(left_timestamp)

    if right_timestamp is not None:
        end_timestamp = _get_readable_timestamp(right_timestamp)

    attrs_str = attrs.display_attributes(tags, t_error)

    row = [
        segment_id,
        user_name if user_name is not None else file_info.user_id,
        updated_at,
        begin_timestamp if left_timestamp is not None else None,
        end_timestamp if right_timestamp is not None else None,
        attrs_str if attrs_str is not None else None,
        sly.app.widgets.Table.create_button(EDIT_BTN),
        sly.app.widgets.Table.create_button(COL_PREVIEW),
        sly.app.widgets.Table.create_button(COL_DELETE),
    ]
    return row


def _get_readable_timestamp(total_seconds):
    timestamp = str(datetime.timedelta(seconds=total_seconds))
    timestamp_div = timestamp.split(".")
    if len(timestamp_div) == 1:
        return timestamp
    return timestamp[:-5]


def _get_timestamp_from_str(str):
    hms = str.split(":")
    total_seconds = int(hms[0]) * 3600 + int(hms[1]) * 60 + float(hms[2])
    return total_seconds


def _close_video_pair():
    if select_videos.pairs_dir_name is not None:
        sly.fs.clean_dir(select_videos.pairs_dir_name)
    card.hide()
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
    attrs.card.hide()


def _get_readable_datetime(value: str) -> str:
    dt = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")

    current_datetime = dt.strftime("%d %B %Y  %H:%M:%S")
    return current_datetime
