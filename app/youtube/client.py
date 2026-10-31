"""YouTube API client wrapper."""

from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from app.config.settings import Settings
from app.metadata.schemas import VideoMetadata

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeClient:
    """Handles OAuth and upload requests to YouTube Data API."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _load_credentials(self) -> Credentials:
        token_file = Path(self.settings.youtube_token_file)
        creds: Credentials | None = None
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

        if creds and creds.valid:
            return creds

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(self.settings.youtube_client_secret, SCOPES)
            creds = flow.run_local_server(port=0)

        token_file.write_text(creds.to_json(), encoding="utf-8")
        return creds

    def upload_video(
        self,
        video_path: Path,
        metadata: VideoMetadata,
        thumbnail_path: Path | None = None,
        publish_at: datetime | None = None,
    ) -> str:
        """Upload a video and return the created YouTube video id."""

        credentials = self._load_credentials()
        youtube = build("youtube", "v3", credentials=credentials)

        body = {
            "snippet": {
                "title": metadata.title,
                "description": metadata.description,
                "tags": metadata.tags,
                "categoryId": "22",
                "defaultLanguage": metadata.language,
            },
            "status": {"privacyStatus": metadata.visibility, "selfDeclaredMadeForKids": False},
        }

        if publish_at and metadata.visibility == "private":
            body["status"]["publishAt"] = publish_at.isoformat() + "Z"

        media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()
        video_id = response["id"]

        if thumbnail_path and thumbnail_path.exists():
            youtube.thumbnails().set(videoId=video_id, media_body=str(thumbnail_path)).execute()

        return video_id
