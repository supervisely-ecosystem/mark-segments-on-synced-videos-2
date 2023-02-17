import io
import json
import os
import supervisely as sly

import src.globals as g
import src.ui.team_files as team_files

NOTE_CONTENT = {
    "app_name": "Mark attributed segments on multi-camera videos",
    "path_in_team_files": "",
    "team_id": g.team_id,
    "project_id": g.project_id,
    "project_name": g.project_info.name,
    "dataset_ids": [],
    "dataset_names": [],
    "videos_count": 0,
}


app_path = os.path.join(g.data_dir, "mark-segments-on-synced-videos-2-files")
if "mark-segments-on-synced-videos-2-files" not in os.listdir(g.data_dir):
    os.mkdir(app_path)
else:
    sly.fs.remove_dir(app_path)
    os.mkdir(app_path)

pr_path = os.path.join(app_path, f"project-{g.project_info.id}")
if f"project-{g.project_info.id}" not in os.listdir(app_path):
    os.mkdir(pr_path)
else:
    sly.fs.remove_dir(pr_path)
    os.mkdir(pr_path)

ds_path = ""


def create_ds_dir():
    global ds_path
    ds_infos = [g.dataset_info]
    ds_ids = [g.dataset_id]
    ds_names = [g.dataset_info.name]
    videos_count = g.dataset_info.items_count
    ds_dir_name = f"dataset-{g.dataset_id}"
    if g.extra_dataset_id:
        ds_infos.append(g.extra_dataset_info)
        ds_ids.append(g.extra_dataset_id)
        ds_names.append(g.extra_dataset_info.name)
        videos_count += g.extra_dataset_info.items_count
        ds_dir_name = f"datasets-{g.dataset_id}-{g.extra_dataset_id}"
        reversed_ds_dir_name = f"datasets-{g.extra_dataset_id}-{g.dataset_id}"
        reversed_ds_dir_path = os.path.join(pr_path, reversed_ds_dir_name)
        if g.api.file.dir_exists(g.team_id, reversed_ds_dir_path):
            ds_dir_name = reversed_ds_dir_name
    ds_path = os.path.join(pr_path, ds_dir_name)
    NOTE_CONTENT["path_in_team_files"] = ds_path
    NOTE_CONTENT["dataset_ids"] = ds_ids
    NOTE_CONTENT["dataset_names"] = ds_names
    NOTE_CONTENT["videos_count"] = {ds_info.name: ds_info.items_count for ds_info in ds_infos}
    if ds_dir_name not in os.listdir(pr_path):
        os.mkdir(ds_path)
    else:
        sly.fs.remove_dir(ds_path)
        os.mkdir(ds_path)

    note_file_path = os.path.join(ds_path, "Info.json")

    with io.open(note_file_path, "w", encoding="utf-8") as f:
        str_ = json.dumps(NOTE_CONTENT, indent=4, separators=(",", ": "), ensure_ascii=False)
        f.write(str(str_))
    try:
        file_info = None
        if g.api.file.exists(g.team_id, note_file_path):
            g.api.file.remove(g.team_id, note_file_path)
        file_info = g.api.file.upload(g.team_id, note_file_path, note_file_path)
    except:
        pass
    finally:
        if file_info is not None:
            team_files.segments_in_team_files.set(file_info)


def clean_local_video_pair_dir(left_video_id: int, right_video_id: int):
    pairs_dir_name = os.path.join(ds_path, f"video-pair-{left_video_id}-{right_video_id}")
    if f"video-pair-{left_video_id}-{right_video_id}" in os.listdir(ds_path):
        sly.fs.clean_dir(pairs_dir_name)
