from supervisely.app.widgets import Card, Checkbox, Container, Grid, VideoPlayer, VideoThumbnail


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


preview = VideoThumbnail()
preview.hide()

player = VideoPlayer()


card = Card(
    "📹 Video #1",
    "Navigate and tag segments begginings on this video",
    content=Container([preview, player, checkbox_container], direction="vertical"),
    lock_message='Select video in table by clicking 👆 "SET LEFT" button on step 3️⃣',
)
card.lock()
