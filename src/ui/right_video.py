from supervisely.app.widgets import Button, Card, Container
from supervisely.app.widgets import VideoPlayer, VideoThumbnail

import src.ui.left_video as left_video

preview = VideoThumbnail()
preview.hide()

player = VideoPlayer()

sync_btn = Button("Sync frame from left video", button_type="text", icon="zmdi zmdi-time")
sync_btn.hide()

card = Card(
    "📹 Video #2",
    "Navigate and tag segments endings on this video",
    content=Container([preview, player, sync_btn], direction="vertical"),
    lock_message='Select video in table by clicking 👆 "SET RIGHT" button on step 3️⃣',
)
card.lock()


@sync_btn.click
def sync_with_left():
    left_timestamp = left_video.player.get_current_timestamp()
    player.set_current_timestamp(left_timestamp)
