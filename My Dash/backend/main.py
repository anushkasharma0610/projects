from __future__ import annotations

import base64
import json
import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import Cookie, Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "dashboard.db"
FRONTEND_DIST = ROOT / "frontend" / "dist"
SESSION_DAYS = 14

DEFAULT_LAYOUT = [
    {"id": "clock", "type": "clock", "title": "World clock", "x": 0, "y": 0, "w": 4, "h": 3},
    {"id": "crypto", "type": "crypto", "title": "Crypto prices", "x": 4, "y": 0, "w": 4, "h": 4},
    {"id": "music", "type": "music", "title": "YouTube Music", "x": 8, "y": 0, "w": 4, "h": 4},
    {"id": "notes", "type": "notes", "title": "Notes", "x": 0, "y": 3, "w": 4, "h": 4},
    {"id": "github", "type": "github", "title": "GitHub activity", "x": 4, "y": 4, "w": 4, "h": 3},
]


@contextmanager
def database():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_database() -> None:
    with database() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL COLLATE NOCASE,
            password_hash TEXT NOT NULL, theme TEXT NOT NULL DEFAULT 'dark', created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY, user_id INTEGER NOT NULL, expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS dashboards (
            user_id INTEGER PRIMARY KEY, layout_json TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, content TEXT NOT NULL,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL,
            owner TEXT NOT NULL, name TEXT NOT NULL,
            last_sha TEXT, last_message TEXT, last_commit_at TEXT, last_checked_at TEXT,
            UNIQUE(user_id, owner, name),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)


def password_hash(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return base64.b64encode(salt + digest).decode()


def check_password(password: str, encoded: str) -> bool:
    raw = base64.b64decode(encoded)
    expected = hashlib.scrypt(password.encode(), salt=raw[:16], n=2**14, r=8, p=1)
    return hmac.compare_digest(raw[16:], expected)


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=40, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)


class Settings(BaseModel):
    theme: str = Field(pattern="^(light|dark)$")


class Layout(BaseModel):
    widgets: list[dict[str, Any]] = Field(max_length=20)


class NoteIn(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class RepositoryIn(BaseModel):
    repository: str = Field(min_length=3, max_length=200, pattern=r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


app = FastAPI(title="My Dash API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


def current_user(session: str | None = Cookie(default=None)) -> sqlite3.Row:
    if not session:
        raise HTTPException(401, "Please sign in")
    with database() as db:
        row = db.execute("""SELECT users.* FROM sessions JOIN users ON users.id = sessions.user_id
                         WHERE sessions.token = ? AND sessions.expires_at > ?""",
                         (session, datetime.now(timezone.utc).isoformat())).fetchone()
    if not row:
        raise HTTPException(401, "Your session has expired")
    return row


def create_session(response: Response, user_id: int) -> None:
    token = secrets.token_urlsafe(32)
    expiry = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    with database() as db:
        db.execute("INSERT INTO sessions(token, user_id, expires_at) VALUES (?, ?, ?)",
                   (token, user_id, expiry.isoformat()))
    response.set_cookie("session", token, httponly=True, samesite="lax", secure=False,
                        max_age=SESSION_DAYS * 86400)


@app.on_event("startup")
def startup() -> None:
    init_database()


@app.post("/api/auth/signup")
def signup(body: Credentials, response: Response):
    username = body.username.strip()
    with database() as db:
        try:
            cursor = db.execute("INSERT INTO users(username, password_hash, created_at) VALUES (?, ?, ?)",
                                (username, password_hash(body.password), datetime.now(timezone.utc).isoformat()))
            user_id = cursor.lastrowid
            db.execute("INSERT INTO dashboards(user_id, layout_json) VALUES (?, ?)",
                       (user_id, __import__("json").dumps(DEFAULT_LAYOUT)))
        except sqlite3.IntegrityError:
            raise HTTPException(409, "That username is already taken")
    create_session(response, user_id)
    return {"id": user_id, "username": username, "theme": "dark"}


@app.post("/api/auth/signin")
def signin(body: Credentials, response: Response):
    with database() as db:
        user = db.execute("SELECT * FROM users WHERE username = ?", (body.username.strip(),)).fetchone()
    if not user or not check_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Incorrect username or password")
    create_session(response, user["id"])
    return {"id": user["id"], "username": user["username"], "theme": user["theme"]}


@app.post("/api/auth/signout", status_code=204)
def signout(response: Response, session: str | None = Cookie(default=None)):
    if session:
        with database() as db:
            db.execute("DELETE FROM sessions WHERE token = ?", (session,))
    response.delete_cookie("session")


@app.get("/api/me")
def me(user: sqlite3.Row = Depends(current_user)):
    return {"id": user["id"], "username": user["username"], "theme": user["theme"]}


@app.patch("/api/me/settings")
def update_settings(body: Settings, user: sqlite3.Row = Depends(current_user)):
    with database() as db:
        db.execute("UPDATE users SET theme = ? WHERE id = ?", (body.theme, user["id"]))
    return {"theme": body.theme}


@app.get("/api/dashboard")
def dashboard(user: sqlite3.Row = Depends(current_user)):
    with database() as db:
        row = db.execute("SELECT layout_json FROM dashboards WHERE user_id = ?", (user["id"],)).fetchone()
    return {"widgets": json.loads(row["layout_json"] if row else "[]")}


@app.put("/api/dashboard")
def save_dashboard(body: Layout, user: sqlite3.Row = Depends(current_user)):
    with database() as db:
        db.execute("""INSERT INTO dashboards(user_id, layout_json) VALUES (?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET layout_json=excluded.layout_json""",
                   (user["id"], json.dumps(body.widgets)))
    return {"widgets": body.widgets}


@app.get("/api/notes")
def get_notes(user: sqlite3.Row = Depends(current_user)):
    with database() as db:
        rows = db.execute("SELECT id, content, created_at, updated_at FROM notes WHERE user_id = ? ORDER BY updated_at DESC",
                          (user["id"],)).fetchall()
    return [dict(row) for row in rows]


@app.post("/api/notes", status_code=201)
def add_note(body: NoteIn, user: sqlite3.Row = Depends(current_user)):
    now = datetime.now(timezone.utc).isoformat()
    with database() as db:
        cursor = db.execute("INSERT INTO notes(user_id, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
                            (user["id"], body.content.strip(), now, now))
    return {"id": cursor.lastrowid, "content": body.content.strip(), "created_at": now, "updated_at": now}


@app.patch("/api/notes/{note_id}")
def update_note(note_id: int, body: NoteIn, user: sqlite3.Row = Depends(current_user)):
    with database() as db:
        changed = db.execute("UPDATE notes SET content = ?, updated_at = ? WHERE id = ? AND user_id = ?",
                             (body.content.strip(), datetime.now(timezone.utc).isoformat(), note_id, user["id"])).rowcount
    if not changed:
        raise HTTPException(404, "Note not found")
    return {"id": note_id, "content": body.content.strip()}


@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: int, user: sqlite3.Row = Depends(current_user)):
    with database() as db:
        db.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user["id"]))


@app.get("/api/crypto")
async def crypto(ids: str = "bitcoin,ethereum,solana,binancecoin", _: sqlite3.Row = Depends(current_user)):
    coin_ids = ",".join(item for item in ids.split(",") if item.replace("-", "").isalnum())
    if not coin_ids:
        return []
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            result = await client.get("https://api.coingecko.com/api/v3/coins/markets", params={
                "vs_currency": "usd", "ids": coin_ids, "price_change_percentage": "24h"})
            result.raise_for_status()
            return result.json()
    except httpx.HTTPError:
        return []


@app.get("/api/crypto/search")
async def search_crypto(q: str = "", _: sqlite3.Row = Depends(current_user)):
    if not q.strip():
        return []
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            result = await client.get("https://api.coingecko.com/api/v3/search", params={"query": q.strip()})
            result.raise_for_status()
            return [
                {"id": coin["id"], "name": coin["name"], "symbol": coin["symbol"]}
                for coin in result.json().get("coins", [])[:8]
            ]
    except httpx.HTTPError:
        return []


async def latest_repository_commit(owner: str, name: str) -> dict[str, str]:
    try:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "My-Dash repository monitor"}
        async with httpx.AsyncClient(timeout=8, headers=headers) as client:
            result = await client.get(f"https://api.github.com/repos/{owner}/{name}/commits", params={"per_page": 1})
            result.raise_for_status()
            commit = result.json()[0]
            return {
                "sha": commit["sha"],
                "message": commit["commit"]["message"].split("\n", 1)[0],
                "committed_at": commit["commit"]["committer"]["date"],
            }
    except httpx.HTTPStatusError as error:
        status = error.response.status_code
        if status == 404:
            raise HTTPException(404, f"{owner}/{name} was not found or is private.")
        if status == 403:
            raise HTTPException(503, "GitHub rate limit reached. Try checking again in a few minutes.")
        raise HTTPException(502, f"GitHub could not return commits for {owner}/{name}.")
    except (httpx.HTTPError, IndexError, KeyError):
        raise HTTPException(502, f"Could not connect to GitHub for {owner}/{name}.")


@app.get("/api/music/search")
async def search_music(q: str = "", _: sqlite3.Row = Depends(current_user)):
    """Resolve a search into a playable YouTube video without requiring an API key."""
    query = q.strip()
    if not query:
        raise HTTPException(400, "Enter a song, artist, or album")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; My-Dash/1.0)", "Accept-Language": "en-US,en;q=0.9"}
        async with httpx.AsyncClient(timeout=10, headers=headers, follow_redirects=True) as client:
            result = await client.get("https://www.youtube.com/results", params={"search_query": query})
            result.raise_for_status()
        match = re.search(r'"videoId":"([A-Za-z0-9_-]{11})"', result.text)
        if not match:
            raise HTTPException(502, "No playable result was found. Try a more specific search.")
        return {"video_id": match.group(1), "query": query}
    except HTTPException:
        raise
    except httpx.HTTPError:
        raise HTTPException(502, "YouTube search is temporarily unavailable.")


@app.get("/api/repositories")
def get_repositories(user: sqlite3.Row = Depends(current_user)):
    with database() as db:
        rows = db.execute("""SELECT id, owner, name, last_sha, last_message, last_commit_at, last_checked_at
                           FROM repositories WHERE user_id = ? ORDER BY owner, name""", (user["id"],)).fetchall()
    return [dict(row) for row in rows]


@app.post("/api/repositories", status_code=201)
async def add_repository(body: RepositoryIn, user: sqlite3.Row = Depends(current_user)):
    owner, name = body.repository.strip().split("/", 1)
    commit = await latest_repository_commit(owner, name)
    checked_at = datetime.now(timezone.utc).isoformat()
    with database() as db:
        try:
            cursor = db.execute("""INSERT INTO repositories(user_id, owner, name, last_sha, last_message, last_commit_at, last_checked_at)
                                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                (user["id"], owner, name, commit["sha"], commit["message"], commit["committed_at"], checked_at))
        except sqlite3.IntegrityError:
            raise HTTPException(409, "That repository is already being monitored")
    return {"id": cursor.lastrowid, "owner": owner, "name": name, "last_sha": commit["sha"],
            "last_message": commit["message"], "last_commit_at": commit["committed_at"], "last_checked_at": checked_at}


@app.post("/api/repositories/check")
async def check_repositories(user: sqlite3.Row = Depends(current_user)):
    with database() as db:
        rows = db.execute("SELECT * FROM repositories WHERE user_id = ?", (user["id"],)).fetchall()
    changed_ids: list[int] = []
    for repo in rows:
        try:
            commit = await latest_repository_commit(repo["owner"], repo["name"])
        except HTTPException:
            continue
        checked_at = datetime.now(timezone.utc).isoformat()
        changed = repo["last_sha"] != commit["sha"]
        with database() as db:
            db.execute("""UPDATE repositories SET last_sha=?, last_message=?, last_commit_at=?, last_checked_at=? WHERE id=?""",
                       (commit["sha"], commit["message"], commit["committed_at"], checked_at, repo["id"]))
        if changed:
            changed_ids.append(repo["id"])
    return {"changed_ids": changed_ids}


@app.delete("/api/repositories/{repository_id}", status_code=204)
def delete_repository(repository_id: int, user: sqlite3.Row = Depends(current_user)):
    with database() as db:
        db.execute("DELETE FROM repositories WHERE id = ? AND user_id = ?", (repository_id, user["id"]))


if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
