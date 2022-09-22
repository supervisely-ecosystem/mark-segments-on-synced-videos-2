<div align="center" markdown>

<img alt="poster" src="https://user-images.githubusercontent.com/12828725/191542318-969707da-63e6-418d-b902-8e3c7ddfd394.png"/>

# Mark segments on video pairs

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-to-Use">How to use</a> •
  <a href="#Demo">Screenshot</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/mark-segments-on-synced-videos)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/mark-segments-on-synced-videos)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/mark-segments-on-synced-videos)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/mark-segments-on-synced-videos.png)](https://supervise.ly)

</div>

# Overview

Application allows tag and manage segments on video pairs in side-by-side view. 

In can work in two modes:
- label segemnt on a single video
- label segment on two videos (pair)

Segment defines by two tags: app assigns tag with string value `begin-<segment-id>` on a specific frame on the left video and  tag with string value `end-<segment-id>` on a specific frame on the right video.

# How to use

1. Run application from the context menu of video dataset
2. Open app
3. **Step 1** shows the information about selected dataset with links to project / dataset.
4. **Step 2** allows to select existing key-value(str) tag or create a new one.
5. On **Step 3** it is needed to select left and right video by clicking on corresponding buttons in videos table.
6. Once videos are selected user can preview and manage existing segments. 
7. Press `Start segments tagging` button to start tagging, i.e. create or delete tags segments.
8. On videos table at **Step 2** there is also column `STATUS` that helps to navigate what videos are finished and what are in progress.

# Screenshot

<img src="https://user-images.githubusercontent.com/12828725/191545391-54bd1189-7a74-4501-a708-0851203c9c07.png">
