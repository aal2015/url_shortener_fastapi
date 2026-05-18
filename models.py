from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime


class ShortURL(Base):
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True, index=True)

    long_url = Column(String, nullable=False)

    short_code = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    expiration_date = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )