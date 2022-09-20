import pandas as pd
import supervisely as sly
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.widgets import Card, Table
import src.globals as g
import src.ui.left_video as left_video
import src.ui.right_video as right_video
import src.ui.tagging as tagging

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

card = Card(
    "3️⃣ Select left and right video",
    "Select different videos for left and right panels. To mark segments on single video just select same video for both panels",
    collapsable=True,
    lock_message=START_LOCK_MESSAGE,
    content=table,
)
card.lock()


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
    g.api.video.get_info_by_id(video_id)
    if datapoint.button_name == COL_SET_LEFT:
        left_video.player.set_video(video_id)
        left_video.preview.set_video_id(video_id)
        left_video.preview.show()
        left_video.card.unlock()
    elif datapoint.button_name == COL_SET_RIGHT:
        right_video.player.set_video(video_id)
        right_video.preview.set_video_id(video_id)
        right_video.preview.show()
        right_video.sync_btn.show()
        right_video.card.unlock()

    if left_video.player.video_id is not None and right_video.player.video_id is not None:
        tagging.show_segments_btn.enable()
        tagging.help_text.hide()


def set_video_status(video_id, existing_tags: sly.VideoTagCollection, value, update=False):
    status_tag = g.get_status_tag()
    existing_tag = existing_tags.get_single_by_name(status_tag.name)
    if existing_tag is None:
        tag = sly.VideoTag(status_tag, value)
        g.api.video.tag.add(video_id, tag)
        table.update_cell_value(COL_ID, video_id, COL_STATUS, value)
    elif update is True:
        g.api.video.tag.update_value(existing_tag.sly_id, value)
