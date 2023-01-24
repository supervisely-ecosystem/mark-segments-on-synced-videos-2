from supervisely.app.widgets import Button, Card, Container, Field, Flexbox
from supervisely.app.widgets import InputNumber, Text, VideoPlayer, VideoThumbnail

import src.ui.left_video as left_video

preview = VideoThumbnail()
preview.hide()

player = VideoPlayer()


seconds_input = InputNumber(min=0.1, max=1000, step=0.1, size="small", controls=True)

fast_forward_btn = Button(text="", button_size="mini", icon="zmdi zmdi-fast-forward", icon_gap=0)
fast_forward_box = Flexbox(widgets=[fast_forward_btn], gap=0)

fast_rewind_btn = Button(text="", button_size="mini", icon="zmdi zmdi-fast-rewind", icon_gap=0)
fast_rewind_box = Flexbox(widgets=[fast_rewind_btn], gap=0)

seconds_text = Text(
    text='<span style="display: flex; align-items: center; height: 100%; color: #7f858e;">seconds</span>'
)

control_box = Flexbox(
    widgets=[fast_rewind_box, fast_forward_box, seconds_input, seconds_text], gap=15
)

navigation_field = Field(
    content=control_box,
    title="Video navigation",
    description="Skip forward and back (in seconds)",
)


sync_btn = Button("Sync timestamp from left video", button_type="text", icon="zmdi zmdi-time")


navigation_field.hide()
sync_btn.hide()

card = Card(
    "📹 Video #2",
    "Navigate and tag segments endings on this video",
    content=Container([preview, player, navigation_field, sync_btn], direction="vertical"),
    lock_message='Select video in table by clicking 👆 "SET RIGHT" button on step 3️⃣',
)
card.lock()


@sync_btn.click
def sync_with_left():
    left_timestamp = left_video.player.get_current_timestamp()
    player.set_current_timestamp(left_timestamp)


@fast_forward_btn.click
def fast_forward_video():
    step = seconds_input.get_value()
    if player.url is None:
        return
    currrent_time = player.get_current_timestamp()
    player.set_current_timestamp(currrent_time + step)


@fast_rewind_btn.click
def fast_rewind_video():
    step = seconds_input.get_value()
    if player.url is None:
        return
    currrent_time = player.get_current_timestamp()
    player.set_current_timestamp(currrent_time - step)
