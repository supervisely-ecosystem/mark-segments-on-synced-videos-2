import supervisely as sly
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.widgets import (
    Card,
    Container,
    SelectTagMeta,
    Input,
    Button,
    Flexbox,
)
import src.globals as g


select_tag = SelectTagMeta(show_label=False, allowed_types=[sly.TagValueType.ANY_STRING])
create_tag_btn = Button("Create new tag", button_type="text", icon="zmdi zmdi-plus", icon_gap=0)
existing_tag_layout = Flexbox([select_tag, create_tag_btn])

input_name = Input("my-event")
save_tag_btn = Button("Save tag", button_type="text", icon="zmdi zmdi-floppy", icon_gap=0)
cancel_tag_btn = Button("Cancel", button_type="text", icon="zmdi zmdi-close", icon_gap=0)
new_tag_layout = Flexbox([input_name, save_tag_btn, cancel_tag_btn])
new_tag_layout.hide()

layout = Card(
    "2️⃣ Select Tag",
    "Select key-value(str) tag for labeling",
    content=Container([existing_tag_layout, new_tag_layout], gap=0),
)


@create_tag_btn.click
def create_tag():
    existing_tag_layout.hide()
    new_tag_layout.show()


@save_tag_btn.click
def save_tag():
    name = input_name.get_value().strip()
    if name == "":
        raise DialogWindowError(
            title="Tag name is empty",
            description="Please, provide the correct tag name.",
        )

    tag_meta = g.project_meta.get_tag_meta(name)
    if tag_meta is not None:
        raise DialogWindowError(
            title="Name already exists",
            description=f"Tag with the name {name} already exists in project. Please, provide another name.",
        )

    print(name)
    # new_tag_layout.hide()
    # existing_tag_layout.show()


@cancel_tag_btn.click
def cancel_tag():
    new_tag_layout.hide()
    existing_tag_layout.show()
