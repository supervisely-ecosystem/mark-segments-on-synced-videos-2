from supervisely.app.widgets import Button, Card, Container, Field, Flexbox
from supervisely.app.widgets import InputNumber, Text, VideoPlayer, VideoThumbnail

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
navigation_field.hide()

card = Card(
    "📹 Video #1",
    "Navigate and tag segments begginings on this video",
    content=Container([preview, player, navigation_field], direction="vertical"),
    lock_message='Select video in table by clicking 👆 "SET LEFT" button on step 3️⃣',
)
card.lock()


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
