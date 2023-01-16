from supervisely.app.widgets import Card, Container, FolderThumbnail

segments_in_team_files = FolderThumbnail()
folder_container = Container(widgets=[segments_in_team_files])

card = Card(
    "📁 Segments in Team files",
    "All created segments will be saved as json files in the appropriate folders for each pair of videos.",
    collapsable=True,
    content=folder_container,
)
