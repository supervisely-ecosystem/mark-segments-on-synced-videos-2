import os
from shutil import rmtree

import src.globals as g

pr_path = os.path.join(g.DATA_DIR, f"project-{g.project_info.id}")
if f"project-{g.project_info.id}" not in os.listdir(g.DATA_DIR):
    os.mkdir(pr_path)
else:
    rmtree(pr_path)
    os.mkdir(pr_path)

ds_path = os.path.join(pr_path, f"dataset-{g.dataset_info.id}")
if f"dataset-{g.dataset_info.id}" not in os.listdir(pr_path):
    os.mkdir(ds_path)
else:
    rmtree(ds_path)
    os.mkdir(ds_path)


def clean_local_video_pair_dir(left_video_id: int, right_video_id: int):
    pairs_dir_name = os.path.join(ds_path, f"video-pair-{left_video_id}-{right_video_id}")
    if f"video-pair-{left_video_id}-{right_video_id}" in os.listdir(ds_path):
        rmtree(pairs_dir_name)
