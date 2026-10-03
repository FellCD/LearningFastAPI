from pydantic import BaseModel

# Schemas de Playlist
class PlaylistCreate(BaseModel):
    playlist_name: str

class PlaylistUpdate(BaseModel):
    playlist_name: str | None
