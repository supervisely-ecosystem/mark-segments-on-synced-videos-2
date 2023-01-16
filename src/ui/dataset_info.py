from supervisely.app.widgets import Card, DatasetThumbnail
import src.globals as g

card = Card(
    "1️⃣ Selected dataset",
    "Label video or pair of videos in current dataset",
    content=DatasetThumbnail(g.project_info, g.dataset_info),
)
