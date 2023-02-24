<div align="center" markdown>

<img src="https://user-images.githubusercontent.com/115161827/211619537-9c5cda6a-788c-4baa-b27e-6a6800e6fdbe.png"/>

# Mark attributed segments on multi-camera videos

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-to-Use">How to use</a> •
  <a href="#Demo-data">Demo data</a> •
  <a href="#Demo">Screenshot</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/mark-segments-on-synced-videos-2)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/mark-segments-on-synced-videos-2)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/mark-segments-on-synced-videos-2)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/mark-segments-on-synced-videos-2.png)](https://supervise.ly)

</div>

# Overview

Application allows tag and manage segments on video pairs in side-by-side view.

It can work in two modes:

- label segment on a single video (same video at left and right video players)
- label segment on two videos (pair)

App assigns to segments identifiers, attributes (tags), timestamps (for left and right videos) and saves in team files as a json file.

**Updates:**

- `v1.0.10` - Added a new information widget that shows where segments are stored in Team Files for the selected video pair.
- `v1.0.11` - Added video control buttons for easier video navigation.
- `v1.0.12` - Changed table sorting settings and added the ability to load videos from multiple datasets.
- `v1.0.13` - Updated the app launching settings to improve performance.
- `v1.0.14` - Added a new feature for drawing masks with regions on videos.

# How to use

0. **Add project tags to the project.** You can create all type of project tags: `none`, `any string`, `any number` and `one of string`. All created tags can be used in the app to add segment attributes (except technical tag `status-segments-on-synced-videos`).

   > It is recommended not to change existing tags. To use the tags in the app correctly, you should prepare tags before launching the app.
   > You can also add new tags later (don’t use existing or removed tag names). Just restart the app to use created tags.

1. Run app from Ecosystem or video project / video dataset context menu.
2. Open app
3. **Step 1** Select one or two datasets to load videos from them. After selecting datasets, it shows the information about selected dataset (or datasets) and a path to segments stored in Team files.
4. **Step 2** It is needed to select left and right video by clicking on corresponding buttons in videos table.
5. After selecting the videos, click on the `draw regions on video` button to display a mask with figures.

   > Here is the algorithm for creating masks with regions on a video:
   >
   > 1. Create the required number of classes (as many as the number of region names needed).
   > 2. Open [Supervisely video labeling tool](https://ecosystem.supervise.ly/apps/video-labeling-tool?_ga=2.61496805.83358356.1676836201-1574751671.1670221597).
   > 3. Select the class with the required region name.
   > 4. Draw the required number of regions on the first frame of the video."
   > 5. If you created new classes, you may need to restart the app for the changes to take effect.
6. Press `SHOW ALL SEGMENTS` button to preview and manage existing segments.
7. Press `START SEGMENTS TAGGING` button to start tagging, i.e. create or delete tags segments.
8. On videos table at **Step 2** there is also column `STATUS` that helps to navigate which videos are finished and which are in progress (press `MARK VIDEOS AS DONE` button).
9. **Step 3** Press `EDIT` button on segments table to manage attributes of selected segment.
10. **Step 4** Change and save segment attributes (press `SAVE` button).
11. Stop the app manually.

**Structure of folders in Team files in which segments will be stored:**

```
TEAM FILES
├── ...
├── sly-app-data
│     └── mark-segments-on-synced-videos-2-files
│           ├── project-<project_id>
│           │   ├── dataset-<dataset_id>
│           │   │   ├── video-pair-<left_video_id>-<right_video_id>
│           │   │   │   ├──segment-1.json
│           │   │   │   ├──segment-2.json
│           │   │   │   └── ...
│           │   │   ├── ...
│           │   ├── datasets-<first_dataset_id>-<second_dataset_id>
│           │   │   ├── video-pair-<left_video_id>-<right_video_id>
│           │   │   │   ├──segment-3.json
│           │   │   │   ├──segment-4.json
│           │   │   │   └── ...
│           │   │   ├── ...
│           │   ├── ...
│           │   ├── ...
│           │   ├── left_player_regions.png  # temp image for drawing mask with regions on videos
│           │   └── right_player_regions.png  # temp image for drawing mask with regions on videos
│           └── ...
└── ...
```

**Structure of json files that store segment data:**

```
{
    "left_video": {
        "id": 17546758,
        "name": "video-01-cam1.mp4",
        "timestamp": 9.6
    },
    "right_video": {
        "id": 17546757,
        "name": "video-01-cam2.mp4",
        "timestamp": 8.5
    },
    "tags": [
        {
            "name": "Missed entry"
        }
    ],
    "created_at": "20 February 2023  07:15:20",
    "updated_at": "20 February 2023  07:34:47",
    "user_name": "admin"
}
```

> **Note:**
>
> - All segment attributes are created and added to `TagCollection` object using the meta tags of current project and stored in a file after serialization to json.
> - All segment attributes are extracted from json files and serialized into `TagCollection` object to manage them.

# Demo data

- [Demo video pairs](https://ecosystem.supervise.ly/projects/demo-video-pairs)

  Use this demo data to test this labeling app.

  <img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/demo-video-pairs" src="https://user-images.githubusercontent.com/12828725/191751649-770c75c0-1265-4cac-b83d-7b3155d20081.png"/>

# Screenshot

<img src="https://user-images.githubusercontent.com/79905215/221146415-83cf8975-45a4-4af7-8de4-48b3ef2452af.png">
