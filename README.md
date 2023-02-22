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
-  `v1.0.10` - added new info widget that shows where segments are stored in Team Files for selected video pair.
-  `v1.0.11` -  added video control buttons for easy video navigation.
-  `v1.0.12` -  changed table sorting settings. Added loading videos from multiple datasets.

# How to use

0. **Add project tags to the project.** You can create all type of project tags: `none`, `any string`, `any number` and `one of string`. All created tags can be used in the app to add segment attributes (except technical tag `status-segments-on-synced-videos`).
1. Run application from the context menu of video dataset
2. Open app
3. **Step 1** shows the information about selected dataset with links to project / dataset.
4. **Step 2** it is needed to select left and right video by clicking on corresponding buttons in videos table.
5. Once videos are selected press `SHOW ALL SEGMENTS` button to preview and manage existing segments.
6. Press `START SEGMENTS TAGGING` button to start tagging, i.e. create or delete tags segments.
7. On videos table at **Step 2** there is also column `STATUS` that helps to navigate what videos are finished and what are in progress (press `MARK VIDEOS AS DONE` button).
8. **Step 3** Press `EDIT` button on segments table to manage attributes of selected segment.
9. **Step 4** Change and save segment attributes (press `SAVE` button).
10. Stop the app manually.


> If you perform some tags modification during working with app, just restart it. All created segments will be saved in team files and can be used in the next time the application will be launched.

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
│           │   └── ...
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
    ]
}
```

>**Note:**
>- All segment attributes are created and added to `TagCollection` object using the meta tags of current project and stored in a file after serialization to json.
>- All segment attributes are extracted from json files and serialized into `TagCollection` object to manage them.
>

# Demo data

- [Demo video pairs](https://ecosystem.supervise.ly/projects/demo-video-pairs)

  Use this demo data to test this labeling app.

  <img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/demo-video-pairs" src="https://user-images.githubusercontent.com/12828725/191751649-770c75c0-1265-4cac-b83d-7b3155d20081.png"/>

# Screenshot

<img src="https://user-images.githubusercontent.com/115161827/211636209-cac25857-4205-434c-becf-74e0ec902c1b.png">
