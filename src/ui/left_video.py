import supervisely as sly
from supervisely.app.widgets import (
    Card,
    Video,
)

player = Video()
card = Card(
    "📹 Video #1",
    "Navigate and tag segments begginings on this video",
    content=player,
    lock_message='Slect video in table by clicking 👆 "SET LEFT" button',
)
card.lock()
