from sqlalchemy import Boolean, Column, Integer, String, DateTime

import db

class URL(db.Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    secret_key = Column(String, unique=True, index=True)
    target_url = Column(String, index=True)
    url = Column(String)
    is_active = Column(Boolean, default=True)
    clicks = Column(Integer, default=0)
    expire_datetime = Column(DateTime)