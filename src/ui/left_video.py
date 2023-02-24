import os
import cv2
import numpy as np

import supervisely as sly
from supervisely.app.exceptions import DialogWindowError
from supervisely.app.widgets import Button, Card, Checkbox, Container, Field, Flexbox
from supervisely.app.widgets import InputNumber, Text, VideoPlayer, VideoThumbnail
from supervisely.imaging.font import get_readable_font_size
from supervisely.video_annotation.key_id_map import KeyIdMap

import src.globals as g
import src.ui.files as f

preview = VideoThumbnail()
preview.hide()

player = VideoPlayer()


seconds_input = InputNumber(min=0.1, max=1000, step=0.1, size="small", controls=True)

fast_forward_btn = Button(text="", button_size="mini", icon="zmdi zmdi-fast-forward", icon_gap=0)
fast_forward_box = Flexbox(widgets=[fast_forward_btn], gap=0)

fast_rewind_btn = Button(text="", button_size="mini", icon="zmdi zmdi-fast-rewind", icon_gap=0)
fast_rewind_box = Flexbox(widgets=[fast_rewind_btn], gap=0)

seconds_text = Text(
    text='<span style="display: flex; align-items: center; height: 100%; color: #7f858e;">seconds</span>'
)

draw_figures_checkbox = Checkbox("draw regions on video")
control_box = Flexbox(
    widgets=[fast_rewind_box, fast_forward_box, seconds_input, seconds_text], gap=15
)
navigation_field = Field(
    content=control_box,
    title="Video navigation",
    description="Skip forward and back (in seconds)",
)
video_settings_container = Container(
    widgets=[navigation_field, draw_figures_checkbox],
    direction="horizontal",
    fractions=[2, 1],
)
video_settings_container.hide()

card = Card(
    "📹 Video #1",
    "Navigate and tag segments begginings on this video",
    content=Container([preview, player, video_settings_container], direction="vertical"),
    lock_message='Select video in table by clicking 👆 "SET LEFT" button on step 3️⃣',
)
card.lock()


@fast_forward_btn.click
def fast_forward_video():
    step = seconds_input.get_value()
    if player.url is None:
        return
    currrent_time = player.get_current_timestamp()
    player.set_current_timestamp(currrent_time + step)


@fast_rewind_btn.click
def fast_rewind_video():
    step = seconds_input.get_value()
    if player.url is None:
        return
    currrent_time = player.get_current_timestamp()
    player.set_current_timestamp(currrent_time - step)


@draw_figures_checkbox.value_changed
def draw_figures(value):
    global g
    if value is False:
        player.hide_mask()
        return
    key_id_map = KeyIdMap()
    ann_json = g.api.video.annotation.download(video_id=g.choosed_videos["left_video"].id)
    ann = sly.VideoAnnotation.from_json(
        data=ann_json, project_meta=g.project_meta, key_id_map=key_id_map
    )
    if len(ann.figures) == 0:
        draw_figures_checkbox.uncheck()
        raise DialogWindowError(
            "No regions",
            "There are no figures on first frame of the video. Please add figures in Supervisely label tool",
        )
    height = g.choosed_videos["left_video"].frame_height
    width = g.choosed_videos["left_video"].frame_width
    img = np.zeros((height, width, 4), dtype=np.uint8)

    img[:, :, :] = (0, 0, 0, 0)
    # img[:, :, 3] = 0

    for fig in ann.figures:
        text = fig.parent_object.to_json()["classTitle"]
        red, green, blue = sly.color.random_rgb()

        fig.geometry.draw(img, (red, green, blue, 255), thickness=10)
        # fig.geometry.draw_contour(img, (red, green, blue, 255), thickness=10)

        bbox_center = fig.geometry.to_bbox().center
        col, row = bbox_center.col, bbox_center.row
        font_size = get_readable_font_size((width, height))
        font = sly.image.get_font(font_file_name=None, font_size=font_size)
        t_width, t_height = font.getsize(text)

        cv2.putText(
            img,
            text,
            (int(col - t_width // 2 + 5), row + 3),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.5,
            color=[0, 0, 0, 255],
            thickness=5,
            lineType=cv2.LINE_AA,
        )
        cv2.putText(
            img,
            text,
            (int(col - t_width // 2), row),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.5,
            color=[255, 255, 255, 255],
            thickness=5,
            lineType=cv2.LINE_AA,
        )

    img_path = os.path.join(f.pr_path, "left_player_regions.png")
    cv2.imwrite(img_path, img)
    mask_file_info = g.api.file.upload(g.team_id, img_path, img_path)
    player.draw_mask(mask_file_info.full_storage_url)
