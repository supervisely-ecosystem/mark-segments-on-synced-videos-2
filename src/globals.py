import os
import supervisely as sly

api = sly.Api()


dataset_id = int(os.environ["context.datasetId"])
dataset_info = api.dataset.get_info_by_id(dataset_id, raise_error=True)
project_id = dataset_info.project_id
project_info = api.project.get_info_by_id(project_id)
project_meta = None
status_tag = None


def refresh_project_meta():
    global project_meta
    meta_json = api.project.get_meta(project_id)
    project_meta = sly.ProjectMeta.from_json(meta_json)


refresh_project_meta()


def get_status_tag() -> sly.TagMeta:
    name = "status-segments-on-synced-videos"
    global status_tag, project_meta
    if status_tag is not None:
        return status_tag

    status_tag = project_meta.get_tag_meta(name)
    if status_tag is not None:
        return status_tag

    status_tag = sly.TagMeta(name, sly.TagValueType.ANY_STRING)
    project_meta = project_meta.add_tag_meta(status_tag)
    api.project.update_meta(project_id, project_meta)
    api.project.pull_meta_ids(project_id, project_meta)
    return status_tag
