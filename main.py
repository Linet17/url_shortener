from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from config import settings



import validators, db as db_file, schemas, secrets, models

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/",
    contact={
        "name": settings.CONTACT_NAME,
        "email": settings.CONTACT_EMAIL
    }
)
db_file.Base.metadata.create_all(bind=db_file.engine)

# setup the middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.post("/urls",
tags=["URL"],
response_model=schemas.URLInfo,
status_code=201
)
def create_url(
    url: schemas.URLBase,
    db: Session = Depends(db_file.get_db)
):
    # validate the url
    if not validators.url(url.target_url):
        raise HTTPException(status_code=400,detail="Invalid url" )

    # generate random strings for keys and secret_key
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    key = "".join(secrets.choice(chars) for _ in range(4))
    secret_key = "".join(secrets.choice(chars) for _ in range(8))

    # current time
    current_time = datetime.now()

    # add 5 mins 
    future_time = current_time + timedelta(minutes=5)

    data = models.URL(
        target_url=url.target_url,
        url = f"{settings.BASE_URL}/{key}",
        key=key,
        secret_key=secret_key,
        expire_datetime = future_time
    )

    # save to the database
    db.add(data)
    db.commit()
    db.refresh(data)
    
    return data


@app.get("/urls",
tags=["URL"],
response_model=List[schemas.URLInfo]
)
def urls(
    db: Session = Depends(db_file.get_db)
):
    return db.query(models.URL).all()

@app.get("/{url_key}")
def forward_to_target_url(
        url_key: str,
        request: Request,
        db: Session = Depends(db_file.get_db)
    ):
    db_url: models.URL = (
        db.query(models.URL)
        .filter(models.URL.key == url_key, models.URL.is_active)
        .first()
    )
    if db_url:

        if datetime.now() > db_url.expire_datetime:
            db_url.is_active = False
            db.commit()
            db.refresh(db_url)
            raise HTTPException(status_code=400, detail="Link expired")

        # update the number of clicks on the url
        db_url.clicks += 1
        db.commit()
        db.refresh(db_url)
        return RedirectResponse(db_url.target_url)
    else:
        raise HTTPException(status_code=404, detail="Not found")

