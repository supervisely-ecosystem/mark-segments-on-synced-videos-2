import supervisely as sly
from supervisely.app.widgets import Card, DatasetThumbnail
import src.globals as g

layout = Card(
    "1️⃣ Input dataset",
    "Label video or pair of videos in current dataset",
    content=DatasetThumbnail(g.project_info, g.dataset_info),
)
