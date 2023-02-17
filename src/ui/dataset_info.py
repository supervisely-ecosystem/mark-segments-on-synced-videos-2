from supervisely.app.widgets import Button, Card, Checkbox, Container, Flexbox
from supervisely.app.widgets import DatasetThumbnail, SelectDataset
import src.globals as g
import src.ui.select_videos as select_videos
import src.ui.files as files
import src.ui.team_files as team_files
import src.ui.tagging as t
import src.ui.left_video as left_video
import src.ui.right_video as right_video

select_left_ds = SelectDataset(project_id=g.project_id, compact=True)
select_right_ds = SelectDataset(project_id=g.project_id, compact=True)
select_right_ds.hide()

left_ds_thumbnail = DatasetThumbnail(show_project_name=False)
left_ds_thumbnail.hide()
right_ds_thumbnail = DatasetThumbnail(show_project_name=False)
right_ds_thumbnail.hide()

same_ds_checkbox = Checkbox(content="Use videos from one dataset", checked=True)

select_ds_btn = Button("OK")
reselect_ds_btn = Button("Select other datasets")
reselect_ds_btn.hide()

btn_container = Flexbox(widgets=[select_ds_btn, reselect_ds_btn])

ds_container = Container(widgets=[left_ds_thumbnail, right_ds_thumbnail], direction="horizontal")
select_datasets = Container(widgets=[select_left_ds, select_right_ds], direction="horizontal")

card = Card(
    "1️⃣ Selected dataset",
    "Label video or pair of videos in current dataset",
    content=Container(widgets=[select_datasets, ds_container, btn_container, same_ds_checkbox]),
)


@same_ds_checkbox.value_changed
def check_right_selector(value):
    if value is True:
        select_right_ds.hide()
    else:
        select_right_ds.show()


@select_ds_btn.click
def select_dataset():
    same_ds_checkbox.hide()
    g.dataset_id = select_left_ds.get_selected_id()
    g.dataset_info = g.api.dataset.get_info_by_id(g.dataset_id, raise_error=True)
    select_videos.build_table(select_videos.table, g.dataset_id)
    left_ds_thumbnail.set(g.project_info, g.dataset_info)

    if not same_ds_checkbox.is_checked() and g.dataset_id != select_right_ds.get_selected_id():
        g.extra_dataset_id = select_right_ds.get_selected_id()
        g.extra_dataset_info = g.api.dataset.get_info_by_id(g.extra_dataset_id, raise_error=True)
        select_videos.build_table(select_videos.extra_table, g.extra_dataset_id)
        select_videos.extra_table.show()
        right_ds_thumbnail.set(g.project_info, g.extra_dataset_info)
        select_right_ds.hide()
        right_ds_thumbnail.show()
    else:
        g.extra_dataset_id = None
        g.extra_dataset_info = None
        select_videos.extra_table.hide()
        same_ds_checkbox.check()
        select_right_ds.hide()
    select_left_ds.hide()
    left_ds_thumbnail.show()
    select_ds_btn.hide()
    reselect_ds_btn.show()
    files.create_ds_dir()
    team_files.card.unlock()
    select_videos.card.unlock()
    select_videos.card.uncollapse()


@reselect_ds_btn.click
def allow_reselect_datasets():
    same_ds_checkbox.show()
    same_ds_checkbox.check()
    select_left_ds.show()
    left_ds_thumbnail.hide()
    right_ds_thumbnail.hide()
    select_videos.card.lock()
    team_files.card.lock()
    select_ds_btn.show()
    reselect_ds_btn.hide()
    t.card.hide()
    left_video.card.lock()
    right_video.card.lock()
