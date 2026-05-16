#!/usr/bin/env python3
"""
jwt-notes-cli: A JWT‑authenticated command‑line notes manager.
"""

import datetime
from pathlib import Path
from typing import Optional

import typer
import jwt
from pydantic import BaseSettings, Field, validator

app = typer.Typer()
NOTES_DIR = Path.home() / ".jwt_notes"

class Settings(BaseSettings):
    """Typed configuration loaded from environment variables or a .env file."""

    secret_key: str = Field(..., env="JWT_NOTES_SECRET")
    algorithm: str = "HS256"
    token_expiry_minutes: int = 60

    @validator("secret_key")
    def secret_not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("secret_key must be provided")
        return v

# Load settings – .env is optional but convenient during development
settings = Settings(_env_file=".env")

def _token_path() -> Path:
    return NOTES_DIR / "token.jwt"

def _load_token() -> Optional[dict]:
    """Return the decoded JWT payload or ``None`` if the token is missing/invalid."""
    try:
        token = _token_path().read_text()
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except Exception:
        return None

def _save_token(payload: dict) -> None:
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    _token_path().write_text(token)

def _require_auth() -> None:
    if not _load_token():
        typer.echo("Not authenticated. Run 'login' first.")
        raise typer.Exit(code=1)

@app.command()
def login(username: str = typer.Option(..., prompt=True)) -> None:
    """Create a JWT for *username* and store it locally."""
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.token_expiry_minutes)
    payload = {"sub": username, "exp": expiry}
    _save_token(payload)
    typer.echo(f"Logged in as {username}. Token saved to {_token_path()}")

@app.command()
def logout() -> None:
    """Remove the stored JWT, ending the session."""
    if _token_path().exists():
        _token_path().unlink()
        typer.echo("Logged out.")
    else:
        typer.echo("No active session.")

@app.command()
def add(note: str = typer.Argument(..., help="Note content")) -> None:
    """Add a new note after ensuring the user is authenticated."""
    _require_auth()
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    note_path = NOTES_DIR / f"{ts}.txt"
    note_path.write_text(note)
    typer.echo(f"Note saved to {note_path}")

@app.command()
def list() -> None:
    """List all stored notes (first line preview)."""
    _require_auth()
    if not NOTES_DIR.exists():
        typer.echo("No notes directory found.")
        raise typer.Exit()
    files = sorted(NOTES_DIR.glob("*.txt"))
    if not files:
        typer.echo("No notes saved yet.")
        raise typer.Exit()
    for f in files:
        preview = f.read_text().splitlines()[0][:30]
        typer.echo(f"{f.stem}: {preview}...")

if __name__ == "__main__":
    app()
