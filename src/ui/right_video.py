import supervisely as sly
from supervisely.app.widgets import (
    Card,
    Video,
)

player = Video()
card = Card(
    "📹 Input video #2",
    "Navigate and tag segments endings on this video",
    content=player,
    lock_message='Slect video in table by clicking 👆 "SET RIGHT" button',
)
card.lock()
