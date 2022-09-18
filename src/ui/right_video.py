import supervisely as sly
from supervisely.app.widgets import Card, Video, VideoThumbnail, Container, Button

import src.ui.left_video as left_video

preview = VideoThumbnail()
preview.hide()

player = Video()
sync_btn = Button("Sync frame from left video", button_type="text", icon="zmdi zmdi-time")
sync_btn.hide()

card = Card(
    "📹 Input video #2",
    "Navigate and tag segments endings on this video",
    content=Container([preview, player, sync_btn], direction="vertical"),
    lock_message='Select video in table by clicking 👆 "SET RIGHT" button on step 3️⃣',
)
card.lock()


@sync_btn.click
def sync_with_left():
    left_frame = left_video.player.get_current_frame()
    player.set_current_frame(left_frame)
