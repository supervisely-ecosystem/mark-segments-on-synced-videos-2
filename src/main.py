import os
from dotenv import load_dotenv
import supervisely as sly
from supervisely.app.widgets import Card, Container, Video

# for convenient debug, has no effect in production
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

vid1 = 3267369
vid2 = 3267370

v1 = Video(vid1)
v2 = Video(vid2)

card1 = Card("Input video #1", "Select first video", content=v1)
card2 = Card("Input video #2", "Select second video", content=v2)
input_cards = Container(widgets=[card1, card2], direction="horizontal", gap=15)


card = Card("Tagging", "Description")
layout = Container(widgets=[input_cards, card], direction="vertical", gap=15)


api = sly.Api()
app = sly.Application(layout=layout)
