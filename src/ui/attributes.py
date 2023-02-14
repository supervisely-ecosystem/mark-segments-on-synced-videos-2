import datetime
import io
import json
import os
from pathlib import Path

import supervisely as sly
from supervisely.app.widgets import Button, Card, Container, InputTag, Text
from supervisely.annotation.tag_meta import TagValueType

import src.globals as g
import src.ui.select_videos as select_videos
import src.ui.tagging as t


data = None
current_segment_id = None
t_error_msg = "Tags loading error. See logs."

segment_id_text = Text(text="", status="info")
tag_inputs = [InputTag(t) for t in g.project_meta.tag_metas if t.name != g.technical_tag_name]
save_button = Button(text="Save tags")

tags_container = Container(widgets=tag_inputs)

card = Card(
    "4️⃣  Attributes to segment",
    "Select attributes to mark current segment",
    content=Container(widgets=[segment_id_text, tags_container, save_button], direction="vertical"),
    lock_message='Select segment in table by clicking 👆 "EDIT" button on step 4️⃣',
)
card.hide()


@save_button.click
def set_tags():
    save_button.loading = True
    card.hide()
    t.table.loading = True
    try:
        global data
        if current_segment_id is None or data is None:
            return
        segment_filepath = os.path.join(
            select_videos.pairs_dir_name, f"segment-{current_segment_id}.json"
        )
        updated_tags = sly.TagCollection()
        project_metas_json = g.project_meta.tag_metas.to_json()
        filtered_project_metas_json = list(
            filter(lambda x: x["name"] != g.technical_tag_name, project_metas_json)
        )
        for i, tm_json in enumerate(filtered_project_metas_json):
            tm = g.project_meta.get_tag_meta(tm_json["name"])
            if tag_inputs[i].is_active():
                tag_value = tag_inputs[i].value
                if tag_inputs[i].get_tag_meta().value_type == str(TagValueType.NONE):
                    tag_value = None
                if tag_value == "":
                    continue
                tag = sly.Tag(tm, tag_value)
                updated_tags = updated_tags.add(tag)

        data["tags"] = updated_tags.to_json()

        with io.open(segment_filepath, "w", encoding="utf-8") as f:
            str_ = json.dumps(
                data, indent=4, sort_keys=True, separators=(",", ": "), ensure_ascii=False
            )
            f.write(str(str_))

        g.api.file.remove(g.team_id, segment_filepath)
        g.api.file.upload(g.team_id, segment_filepath, segment_filepath)
        attrs_str = display_attributes(updated_tags)
        t.table.update_cell_value(t.COL_ID, current_segment_id, t.COL_ATTRIBUTES, attrs_str)

    except Exception as e:
        raise sly.logger.error(e, stack_info=False)
    finally:
        t.table.loading = False
        t.card.unlock()
        save_button.loading = False
        data = None
        t.done_tagging_btn.show()
        t.mark_segment_btn.show()
        t.close_pair_btn.show()
        t.start_tagging_btn.hide()


def show_attrs_card(segment_id):
    card.show()
    card._title = f"📹 Attributes to segment-{segment_id}"

    global current_segment_id, data
    data = None
    current_segment_id = segment_id
    segment_filepath = os.path.join(select_videos.pairs_dir_name, f"segment-{segment_id}.json")
    if Path(segment_filepath).exists():
        if Path(segment_filepath).is_file():
            os.remove(segment_filepath)
    project_metas = g.project_meta.tag_metas
    project_metas_json = project_metas.to_json()

    filtered_project_metas = list(
        filter(lambda x: x["name"] != g.technical_tag_name, project_metas_json)
    )
    if g.api.file.exists(g.team_id, segment_filepath):
        g.api.file.download(g.team_id, segment_filepath, segment_filepath)
        with io.open(segment_filepath) as f:
            tags_to_delete = []
            data = json.load(f)
            for tag in data["tags"]:
                tag_meta = g.project_meta.get_tag_meta(tag["name"])
                if tag_meta is None:
                    tags_to_delete.append(tag)
            if len(tags_to_delete) > 0:
                for tag in tags_to_delete:
                    data["tags"].remove(tag)
                    sly.logger.warning(
                        f'Can not load tag "{tag["name"]}". Please contact tech support.'
                    )
            tags = sly.TagCollection.from_json(data["tags"], g.project_meta.tag_metas)
            if len(tags_to_delete) > 0:
                attrs_str = display_attributes(tags, t_error_msg)
                updated_at = datetime.datetime.now().strftime("%d %B %Y  %H:%M:%S")
                t.table.update_cell_value(t.COL_ID, current_segment_id, t.COL_ATTRIBUTES, attrs_str)
                t.table.update_cell_value(t.COL_ID, current_segment_id, t.COL_UPDATED_AT, updated_at)

            for i, tm in enumerate(filtered_project_metas):
                tag_inputs[i].deactivate()
                if tag_inputs[i].get_tag_meta().value_type == str(TagValueType.ANY_NUMBER):
                    tag_inputs[i].value = 0
                if tag_inputs[i].get_tag_meta().value_type == str(TagValueType.ANY_STRING):
                    tag_inputs[i].value = ""

                for tag in tags:
                    if tag.meta.name == tm["name"]:
                        tag_inputs[i].set(tag)
    else:
        for i, tm in enumerate(filtered_project_metas):
            tag_inputs[i].deactivate()
    save_button.loading = False


def display_attributes(tags: sly.TagCollection, t_error: str = None):
    err_str = ""
    attrs = []
    if t_error is not None:
        err_str = f"""<p style='
            margin: 2px;
            padding: 2px;
        '>
            <span style='
                padding: 2px;
                color: red;
                background-color: mistyrose;
                border-radius: 2px;
            '>
                {t_error}
            </span>
        </p>"""
    if len(tags) == 0:
        return err_str
    for tag in tags:
        if tag.name == g.technical_tag_name:
            continue
        elif tag.value is None:
            attrs.append(tag.name)
        else:
            attrs.append(f"{tag.name}: {tag.value}")
    attrs_str = " ".join(
        [
            f"""<p style='
                margin: 2px;
                padding: 2px;
            '>
                <span style='
                    padding: 2px;
                    background-color: antiquewhite;
                    border-radius: 2px;
                '>
                    • {attr}
                </span>
            </p>"""
            for attr in attrs
        ]
    )
    return err_str + attrs_str
