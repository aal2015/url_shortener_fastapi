from pydantic import BaseModel
from datetime import datetime


class ShortURL_Request(BaseModel):
    long_url: str
    custom_alias: str | None = None
    expiration_date: datetime | None = None

class OriginalURL_Response(BaseModel):
    long_url: str