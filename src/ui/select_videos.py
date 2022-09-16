import pandas as pd
import supervisely as sly
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.widgets import Card, Container, SelectTagMeta, Input, Button, Flexbox, Table
import src.globals as g


columns = ["id", "video", "duration", "frames", "set left", "set right", "processed"]
lines = None

table = Table(fixed_cols=1, width="100%")

layout = Card(
    "3️⃣ Select left and right video",
    "Select different videos for left and right panels. To mark segments on single video just select same video for both panels",
    content=table,
)


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
                None,
                None,
                None,
                None,
                None,
            ]
        )
    df = pd.DataFrame(lines, columns=columns)
    table.read_pandas(df)
    table.loading = False
