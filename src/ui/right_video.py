import supervisely as sly
from supervisely.app.widgets import Card, Video, VideoThumbnail, Container

preview = VideoThumbnail()
preview.hide()

player = Video()
card = Card(
    "📹 Input video #2",
    "Navigate and tag segments endings on this video",
    content=Container([preview, player], direction="vertical"),
    lock_message='Select video in table by clicking 👆 "SET RIGHT" button on step 3️⃣',
)
card.lock()
