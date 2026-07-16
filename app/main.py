import os
import secrets

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Demo credentials only — override via env vars in real deployments.
# Still a plaintext compare; swap for a real user store + hashed passwords
# (e.g. passlib/bcrypt) before shipping this anywhere real.
USERNAME = os.environ.get("APP_USERNAME", "admin")
PASSWORD = os.environ.get("APP_PASSWORD", "password123")

# Very small in-memory session store, only so /welcome can be gated.
# Fine for tests/demo; use signed cookies or a real session backend in prod.
_sessions: set[str] = set()
SESSION_COOKIE = "session_id"


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == USERNAME and password == PASSWORD:
        session_id = secrets.token_urlsafe(32)
        _sessions.add(session_id)
        response = RedirectResponse(url="/welcome", status_code=303)
        response.set_cookie(
            SESSION_COOKIE,
            session_id,
            httponly=True,
            samesite="lax",
        )
        return response
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid username or password"}
    )


@app.get("/welcome", response_class=HTMLResponse)
def welcome(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE)
    if not session_id or session_id not in _sessions:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("welcome.html", {"request": request})


@app.get("/health")
def health():
    """Lightweight endpoint for container/CI health checks."""
    return {"status": "ok"}
