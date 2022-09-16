import pandas as pd
import supervisely as sly
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.widgets import Card, Container, SelectTagMeta, Input, Button, Flexbox, Table
import src.globals as g
import src.ui.left_video as left_video
import src.ui.right_video as right_video

columns = ["id", "video", "duration (sec)", "frames", "set left", "set right", "processed"]
lines = None

table = Table(fixed_cols=2, width="100%")

card = Card(
    "Step 3️⃣  Select left and right video",
    "Select different videos for left and right panels. To mark segments on single video just select same video for both panels",
    collapsable=True,
    lock_message="Select labeling tag on step 2️⃣",
    content=table,
)
card.lock()


def build_table():
    global lines, table
    if lines is None:
        lines = []
    table.loading = True
    videos = g.api.video.get_list(g.dataset_id)
    for info in videos:
        labeling_url = sly.video.get_labeling_tool_url(g.dataset_id, info.id)
        lines.append(
            [
                info.id,
                sly.video.get_labeling_tool_link(labeling_url, info.name),
                info.duration,
                info.frames_count_compact,
                sly.app.widgets.Table.create_button("set left"),
                sly.app.widgets.Table.create_button("set right"),
                None,
            ]
        )
    df = pd.DataFrame(lines, columns=columns)
    table.read_pandas(df)
    table.loading = False


@table.click
def handle_table_button(datapoint: sly.app.widgets.Table.ClickedDataPoint):
    if datapoint.button_name is None:
        return
    video_id = datapoint.row["id"]
    g.api.video.get_info_by_id(video_id)
    if datapoint.button_name == "set left":
        left_video.player.set_video(video_id)
        left_video.card.unlock()
    elif datapoint.button_name == "set right":
        right_video.player.set_video(video_id)
        right_video.card.unlock()
