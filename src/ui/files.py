import io
import json
import os
import supervisely as sly

import src.globals as g
import src.ui.team_files as team_files

NOTE_CONTENT = {
    "team_id": g.team_id,
    "project_id": g.project_id,
    "project_name": g.project_info.name,
    "dataset_id": g.dataset_id,
    "dataset_name": g.dataset_info.name,
    "videos_count": g.dataset_info.items_count,
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

ds_path = os.path.join(pr_path, f"dataset-{g.dataset_info.id}")
if f"dataset-{g.dataset_info.id}" not in os.listdir(pr_path):
    os.mkdir(ds_path)
else:
    sly.fs.remove_dir(ds_path)
    os.mkdir(ds_path)

note_file_path = os.path.join(ds_path, "Info.json")

if not g.api.file.exists(g.team_id, note_file_path):
    with io.open(note_file_path, "w", encoding="utf-8") as f:
        str_ = json.dumps(NOTE_CONTENT, indent=4, separators=(",", ": "), ensure_ascii=False)
        f.write(str(str_))
    file_info = g.api.file.upload(g.team_id, note_file_path, note_file_path)
else:
    file_info = g.api.file.get_info_by_path(g.team_id, note_file_path)

team_files.segments_in_team_files.set(file_info)


def clean_local_video_pair_dir(left_video_id: int, right_video_id: int):
    pairs_dir_name = os.path.join(ds_path, f"video-pair-{left_video_id}-{right_video_id}")
    if f"video-pair-{left_video_id}-{right_video_id}" in os.listdir(ds_path):
        sly.fs.clean_dir(pairs_dir_name)
