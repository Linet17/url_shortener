from pydantic import BaseModel
from datetime import datetime

class URLBase(BaseModel):
    target_url: str
    

class URL(URLBase):
    is_active: bool
    clicks: int
    expire_datetime: datetime

    class Config:
        orm_mode = True

class URLInfo(URL):
    url: str
    