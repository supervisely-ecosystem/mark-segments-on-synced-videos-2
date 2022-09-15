import os
from dotenv import load_dotenv
import supervisely as sly
from supervisely.app.widgets import Card

# for convenient debug, has no effect in production
load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

card = Card("Title", "Description")

api = sly.Api()
app = sly.Application(layout=card)
