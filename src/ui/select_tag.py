import supervisely as sly
from supervisely.annotation.tag_meta import TagMeta, TagValueType
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.widgets import (
    Card,
    Container,
    SelectTagMeta,
    Input,
    Button,
    Flexbox,
    Container,
    Text,
)
import src.globals as g
import src.ui.input_dataset as input_dataset
import src.ui.left_video as left_video
import src.ui.right_video as right_video
import src.ui.select_videos as select_videos
import src.ui.tagging as tagging


select_tag = SelectTagMeta(show_label=False, allowed_types=[sly.TagValueType.ANY_STRING])
create_tag_btn = Button("Create new tag", button_type="text", icon="zmdi zmdi-plus", icon_gap=0)
finish_step_btn = Button("Finish step", icon="zmdi zmdi-check")
change_tag_btn = Button("Change", icon="zmdi zmdi-rotate-left")
change_tag_btn.hide()

tag_selected_text = Text("Tag has been successfully selected", status="success")
tag_selected_text.hide()

existing_tag_layout = Container(
    [
        Flexbox([select_tag, create_tag_btn]),
        tag_selected_text,
        finish_step_btn,
    ]
)

input_name = Input("my-event")
save_tag_btn = Button("Save tag", button_type="text", icon="zmdi zmdi-floppy", icon_gap=0)
cancel_tag_btn = Button("Cancel", button_type="text", icon="zmdi zmdi-close", icon_gap=0)


new_tag_layout = Flexbox([input_name, save_tag_btn, cancel_tag_btn])
new_tag_layout.hide()

card = Card(
    "2️⃣ Select Tag",
    "Select key-value(str) tag for labeling",
    collapsable=True,
    content=Container([existing_tag_layout, new_tag_layout], gap=0),
    content_top_right=change_tag_btn,
)


@create_tag_btn.click
def create_tag():
    existing_tag_layout.hide()
    new_tag_layout.show()


def create_tag_meta_and_update_project(tag_meta: TagMeta, raise_existing_error=True):
    existing_tag_meta = g.project_meta.get_tag_meta(tag_meta.name)
    if existing_tag_meta is not None:
        if raise_existing_error is False:
            return existing_tag_meta
        raise DialogWindowError(
            title="Name already exists",
            description=f"Tag with the name {tag_meta.name} already exists in project. Please, create another name.",
        )

    g.project_meta = g.project_meta.add_tag_meta(tag_meta)
    g.api.project.update_meta(g.project_id, g.project_meta)
    g.api.project.pull_meta_ids(g.project_id, g.project_meta)


@save_tag_btn.click
def save_tag():
    name = input_name.get_value().strip()
    if name == "":
        raise DialogWindowError(
            title="Tag name is empty",
            description="Please, provide the correct tag name.",
        )
    tag_meta = TagMeta(name, TagValueType.ANY_STRING)
    create_tag_meta_and_update_project(tag_meta)

    new_tag_layout.hide()
    existing_tag_layout.show()
    select_tag.set_name(name)


@cancel_tag_btn.click
def cancel_tag():
    new_tag_layout.hide()
    existing_tag_layout.show()


@finish_step_btn.click
def finish_step():
    tag_name = select_tag.get_selected_name()
    print(tag_name)
    if tag_name is None:
        raise DialogWindowError(
            title="Tag is not selected",
            description="Please, select existing tag or create a new one before start labeling",
        )
    select_tag.disable()
    create_tag_btn.disable()
    finish_step_btn.hide()
    change_tag_btn.show()
    tag_selected_text.show()
    select_videos.card.unlock()
    select_videos.card.uncollapse()


@change_tag_btn.click
def change_tag():
    select_tag.enable()
    create_tag_btn.enable()
    finish_step_btn.show()
    change_tag_btn.hide()
    tag_selected_text.hide()
    select_videos.card.lock(message=select_videos.START_LOCK_MESSAGE)
    select_videos.card.collapse()
    right_video.card.lock()
    left_video.card.lock()

    tagging.card.lock()
    select_videos.reselect_pair_btn.hide()
    tagging.done_tagging_btn.hide()
    tagging.mark_segment_btn.hide()
    tagging.close_pair_btn.hide()
    tagging.show_segments_btn.show()
    tagging.show_segments_btn.disable()
    tagging.help_text.show()
    tagging.start_tagging_btn.hide()


def get_tag_meta() -> TagMeta:
    working_tag_name = select_tag.get_selected_name()
    working_tag = g.project_meta.get_tag_meta(working_tag_name)
    if working_tag is None:
        raise DialogWindowError(
            f"Tag {working_tag_name} not found in local project_meta object",
            "Please, contact technical support",
        )
    return working_tag
