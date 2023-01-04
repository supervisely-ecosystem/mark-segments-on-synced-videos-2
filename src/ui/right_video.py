from supervisely.app.widgets import Button, Card, Checkbox, Container, Grid
from supervisely.app.widgets import VideoPlayer, VideoThumbnail

import src.ui.left_video as left_video

preview = VideoThumbnail()
preview.hide()

player = VideoPlayer()

sync_btn = Button("Sync frame from left video", button_type="text", icon="zmdi zmdi-time")
sync_btn.hide()


check_is_broken_tag = Checkbox(content="Add broken tag")
check_missed_entry = Checkbox(content="Missed entry")
check_abandoned_queue = Checkbox(content="Abandoned queue")
check_skipped_queue = Checkbox(content="Skipped queue")
check_frozen_entry = Checkbox(content="Frozen video - entry")
check_frozen_exit = Checkbox(content="Frozen video - exit")

checkbox_container = Grid(
    widgets=[
        check_is_broken_tag,
        check_missed_entry,
        check_abandoned_queue,
        check_skipped_queue,
        check_frozen_entry,
        check_frozen_exit,
    ],
    gap=10,
    columns=3,
)
checkbox_container.hide()

card = Card(
    "📹 Video #2",
    "Navigate and tag segments endings on this video",
    content=Container([preview, player, checkbox_container, sync_btn], direction="vertical"),
    lock_message='Select video in table by clicking 👆 "SET RIGHT" button on step 3️⃣',
)
card.lock()


@sync_btn.click
def sync_with_left():
    left_timestamp = left_video.player.get_current_timestamp()
    player.set_current_timestamp(left_timestamp)
