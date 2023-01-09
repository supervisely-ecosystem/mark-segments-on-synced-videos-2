import os
import pandas as pd
import supervisely as sly
from supervisely.app.widgets import Card, Table, Button
from supervisely._utils import abs_url

import src.globals as g
import src.ui.files as f
import src.ui.left_video as left_video
import src.ui.right_video as right_video
import src.ui.tagging as tagging
import src.ui.attributes as attrs


pairs_dir_name = None

COL_ID = "id".upper()
COL_VIDEO = "video".upper()
COL_DURATION = "duration (sec)".upper()
COL_FRAMES = "frames".upper()
COL_SET_LEFT = "set left".upper()
COL_SET_RIGHT = "set right".upper()
COL_STATUS = "status".upper()

columns = [COL_ID, COL_VIDEO, COL_DURATION, COL_FRAMES, COL_SET_LEFT, COL_SET_RIGHT, COL_STATUS]
lines = None
table = Table(fixed_cols=2, width="100%")

START_LOCK_MESSAGE = "Select labeling tag on step 2️⃣"
LABELING_LOCK_MESSAGE = "Stop tagging for current video pair before select another videos"

reselect_pair_btn = Button("Select other videos", icon="zmdi zmdi-rotate-left")
reselect_pair_btn.hide()

card = Card(
    "2️⃣ Select left and right video",
    "Select different videos for left and right panels. To mark segments on single video just select same video for both panels",
    collapsable=True,
    content=table,
    content_top_right=reselect_pair_btn,
    lock_message=START_LOCK_MESSAGE,
)


def build_table():
    global lines, table
    if lines is None:
        lines = []
    status_tag_meta = g.get_status_tag()
    table.loading = True
    videos = g.api.video.get_list(g.dataset_id)
    for info in videos:
        tag_collection = sly.VideoTagCollection.from_api_response(
            info.tags, g.project_meta.tag_metas
        )
        status_tag = tag_collection.get_single_by_name(status_tag_meta.name)
        labeling_url = sly.video.get_labeling_tool_url(g.dataset_id, info.id)
        lines.append(
            [
                info.id,
                sly.video.get_labeling_tool_link(labeling_url, info.name),
                info.duration,
                info.frames_count_compact,
                sly.app.widgets.Table.create_button(COL_SET_LEFT),
                sly.app.widgets.Table.create_button(COL_SET_RIGHT),
                status_tag.value if status_tag is not None else None,
            ]
        )
    df = pd.DataFrame(lines, columns=columns)
    table.read_pandas(df)
    table.loading = False


@table.click
def handle_table_button(datapoint: sly.app.widgets.Table.ClickedDataPoint):
    if datapoint.button_name is None:
        return
    video_id = datapoint.row[COL_ID]
    video_info = g.api.video.get_info_by_id(video_id)
    video_url = abs_url(video_info.path_original)
    video_type = video_info.file_meta["mime"]
    if datapoint.button_name == COL_SET_LEFT:
        g.choosed_videos["left_video"] = video_info
        left_video.player.set_video(url=video_url, mime_type=video_type)
        left_video.preview.set_video_id(video_id)
        left_video.preview.show()
        left_video.card.unlock()
    elif datapoint.button_name == COL_SET_RIGHT:
        g.choosed_videos["right_video"] = video_info
        right_video.player.set_video(url=video_url, mime_type=video_type)
        right_video.preview.set_video_id(video_id)
        right_video.preview.show()
        right_video.sync_btn.show()
        right_video.card.unlock()

    global pairs_dir_name
    if left_video.player.url is not None and right_video.player.url is not None:
        tagging.help_text.hide()
        tagging.show_segments_btn.enable()
        tagging.show_segments_btn.show()
        reselect_pair_btn.show()
        tagging.start_tagging_btn.hide()
        tagging.mark_segment_btn.hide()
        left_video_id = g.choosed_videos["left_video"].id
        right_video_id = g.choosed_videos["right_video"].id
        pairs_dir_name = os.path.join(f.ds_path, f"video-pair-{left_video_id}-{right_video_id}")

        if f"video-pair-{left_video_id}-{right_video_id}" not in os.listdir(f.ds_path):
            os.mkdir(pairs_dir_name)
        print("--", pairs_dir_name)
        print("--", g.api.file.dir_exists(g.TEAM_ID, f"/{pairs_dir_name}"))
        print("--", g.api.file.dir_exists(g.TEAM_ID, pairs_dir_name))
        if not g.api.file.dir_exists(g.TEAM_ID, pairs_dir_name):
            g.api.file.upload_directory(g.TEAM_ID, pairs_dir_name, pairs_dir_name)


def set_video_status(video_id, existing_tags: sly.VideoTagCollection, value, update=False):
    status_tag = g.get_status_tag()
    existing_tag = existing_tags.get_single_by_name(status_tag.name)
    if existing_tag is None:
        tag = sly.VideoTag(status_tag, value)
        g.api.video.tag.add(video_id, tag)
        table.update_cell_value(COL_ID, video_id, COL_STATUS, value)
    elif update is True:
        g.api.video.tag.update_value(existing_tag.sly_id, value)
        table.update_cell_value(COL_ID, video_id, COL_STATUS, value)


@reselect_pair_btn.click
def reselect_video_pair():
    tagging.card.hide()
    tagging.start_tagging_btn.hide()
    tagging.mark_segment_btn.hide()
    tagging.show_segments_btn.show()
    tagging.show_segments_btn.disable()
    tagging.help_text.show()
    tagging.left_video.card.lock()
    tagging.right_video.card.lock()
    tagging.done_tagging_btn.hide()
    tagging.close_pair_btn.hide()
    card.uncollapse()
    card.unlock()
    reselect_pair_btn.hide()
    tagging.start_tagging_btn.hide()
    tagging.mark_segment_btn.hide()
    attrs.card.hide()
