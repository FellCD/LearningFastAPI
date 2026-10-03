from pydantic import BaseModel

# Schemas da Música
class DurationSchema(BaseModel):
    duration_min: int
    duration_sec: int

class SongSchema(BaseModel):
    name: str
    author: str
    duration: DurationSchema

class UpdateSongSchema(BaseModel):
    name: str | None = None
    author: str | None = None
    duration:DurationSchema | None = None