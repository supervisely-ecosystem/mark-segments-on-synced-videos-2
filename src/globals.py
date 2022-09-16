import os
import supervisely as sly

api = sly.Api()


dataset_id = int(os.environ["context.datasetId"])
dataset_info = api.dataset.get_info_by_id(dataset_id, raise_error=True)
project_info = api.project.get_info_by_id(dataset_info.project_id)

meta_json = api.project.get_meta(project_info.id)
project_meta = sly.ProjectMeta.from_json(meta_json)
