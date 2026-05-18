from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import random
import string

from database import engine, Base, get_db
from models import ShortURL
from schemas import ShortURL_Request, OriginalURL_Response

app = FastAPI()

Base.metadata.create_all(bind=engine)

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits

    return ''.join(
        random.choice(characters)
        for _ in range(length)
    )

@app.post("/generateShortURL")
def generate_short_url(
    shortUrl: ShortURL_Request,
    db: Session = Depends(get_db)
):

    # Check if long URL already exists
    existing_long_url = db.query(ShortURL).filter(
        ShortURL.long_url == shortUrl.long_url
    ).first()

    if existing_long_url:
        return {
            "message": "Long URL already exists",
            "short_code": existing_long_url.short_code
        }

    # Use custom alias if provided
    if shortUrl.custom_alias:

        # Check if alias already exists
        existing_alias = db.query(ShortURL).filter(
            ShortURL.short_code == shortUrl.custom_alias
        ).first()

        if existing_alias:
            raise HTTPException(
                status_code=400,
                detail="Custom alias already exists"
            )

        short_code = shortUrl.custom_alias

    else:

        # Generate unique random code
        while True:

            generated_code = generate_short_code()

            existing_code = db.query(ShortURL).filter(
                ShortURL.short_code == generated_code
            ).first()

            if not existing_code:
                short_code = generated_code
                break

    # Save to DB
    new_short_url = ShortURL(
        long_url=shortUrl.long_url,
        short_code=short_code,
        expiration_date=shortUrl.expiration_date
    )

    db.add(new_short_url)

    db.commit()

    db.refresh(new_short_url)

    return {
        "message": "Short URL created",
        "short_code": short_code
    }

@app.get(
    "/getOriginalURL/{short_code}",
    response_model=OriginalURL_Response
)
def get_original_url(
    short_code: str,
    db: Session = Depends(get_db)
):

    short_url = db.query(ShortURL).filter(
        ShortURL.short_code == short_code
    ).first()

    if not short_url:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    return {
        "long_url": short_url.long_url
    }