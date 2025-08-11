import os
from typing import List

from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from . import models, security
from .database import Base, SessionLocal, engine


Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    SessionMiddleware, secret_key=os.environ.get("SESSION_SECRET_KEY", "changeme")
)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_admin():
    db = SessionLocal()
    if not db.query(models.User).first():
        hashed = security.hash_password("admin")
        db.add(models.User(username="admin", hashed_password=hashed))
        db.commit()
    db.close()


init_admin()


def current_user(request: Request, db: Session):
    username = request.session.get("user")
    if username:
        return db.query(models.User).filter(models.User.username == username).first()
    return None


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not security.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid credentials"}, status_code=status.HTTP_401_UNAUTHORIZED
        )
    request.session["user"] = user.username
    return RedirectResponse("/passwords", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/passwords", response_class=HTMLResponse)
async def list_passwords(request: Request, q: str = "", db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    entries_query = db.query(models.PasswordEntry).filter(models.PasswordEntry.owner_id == user.id)
    if q:
        entries_query = entries_query.filter(models.PasswordEntry.site.contains(q))
    entries = entries_query.all()
    decrypted = [
        {
            "site": e.site,
            "username": e.username,
            "password": security.decrypt_text(e.password),
        }
        for e in entries
    ]
    return templates.TemplateResponse(
        "passwords.html", {"request": request, "entries": decrypted, "q": q}
    )


@app.get("/add", response_class=HTMLResponse)
async def add_password_page(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("add_password.html", {"request": request})


@app.post("/add")
async def add_password(
    request: Request,
    site: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    enc = security.encrypt_text(password)
    entry = models.PasswordEntry(site=site, username=username, password=enc, owner_id=user.id)
    db.add(entry)
    db.commit()
    return RedirectResponse("/passwords", status_code=status.HTTP_303_SEE_OTHER)
