from supervisely.app.widgets import Card, Container, VideoPlayer, VideoThumbnail

preview = VideoThumbnail()
preview.hide()

player = VideoPlayer()


card = Card(
    "📹 Video #1",
    "Navigate and tag segments begginings on this video",
    content=Container([preview, player], direction="vertical"),
    lock_message='Select video in table by clicking 👆 "SET LEFT" button on step 3️⃣',
)
card.lock()
