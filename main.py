from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class ShortURL(BaseModel):
    long_url: str
    custom_alias: str | None = None
    expiration_date: datetime | None = None

@app.post("/generateShortURL")
def generate_short_url(shortUrl : ShortURL):
    return {"Hello": "World"}

@app.get("/getOriginalURL")
def get_original_url():
    return {"Hello": "World"}