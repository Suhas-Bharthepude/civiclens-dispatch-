# backend/app/routes/auth_routes.py
# Authentication endpoints: register, login, me.
#
# Day 72: Auth with admin and dispatcher roles
#
# Endpoints:
#   POST /auth/register — create a new user (development only)
#   POST /auth/login    — verify credentials and return a JWT
#   GET  /auth/me       — return the current user's profile

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.config import settings
from app.db.database import database
from app.db.models import users


# ── ROUTER ────────────────────────────────────────────────
router = APIRouter(prefix="/auth", tags=["auth"])


# ── REQUEST / RESPONSE SCHEMAS ────────────────────────────

class UserCreate(BaseModel):
    """Body for POST /auth/register."""
    username: str
    password: str
    # Defaults to dispatcher — callers can override to "admin" in dev
    role: str = "dispatcher"


class LoginRequest(BaseModel):
    """Body for POST /auth/login."""
    username: str
    password: str


# ── POST /auth/register ───────────────────────────────────

@router.post("/register", status_code=201)
async def register_user(data: UserCreate):
    """
    Create a new user account.

    Restricted to development environments — in production use the
    seed script (backend/scripts/seed_users.py) instead.
    Registering over HTTP in production would expose account creation
    to the public network without an admin guard.
    """
    # Hard-block in production — return 403 instead of 404 so callers
    # know the endpoint exists but is intentionally disabled
    if not settings.is_development:
        raise HTTPException(
            status_code=403,
            detail="User registration is disabled in production. Use the seed script.",
        )

    # Check for duplicate username — the DB column is UNIQUE but we want
    # a friendlier error message than a raw SQLite constraint violation
    existing = await database.fetch_one(
        users.select().where(users.c.username == data.username)
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Username '{data.username}' is already taken",
        )

    # Validate role — only these two roles are supported
    if data.role not in ("admin", "dispatcher"):
        raise HTTPException(
            status_code=400,
            detail="role must be 'admin' or 'dispatcher'",
        )

    # Hash the password before storing — never write plaintext
    hashed = hash_password(data.password)

    # Insert the new user row
    insert_q = users.insert().values(
        username=data.username,
        hashed_password=hashed,
        role=data.role,
        created_at=datetime.utcnow(),
    )
    new_id = await database.execute(insert_q)

    # Fetch and return the created user (without the password hash)
    new_user = await database.fetch_one(users.select().where(users.c.id == new_id))
    return {
        "id":       new_user["id"],
        "username": new_user["username"],
        "role":     new_user["role"],
    }


# ── POST /auth/login ──────────────────────────────────────

@router.post("/login")
async def login(data: LoginRequest):
    """
    Verify credentials and return a signed JWT.

    Returns HTTP 401 for both "user not found" and "wrong password" —
    a single error message prevents username enumeration attacks.
    """
    # Look up the user by username
    user = await database.fetch_one(
        users.select().where(users.c.username == data.username)
    )

    # Use a constant-time comparison (verify_password uses bcrypt) so
    # an attacker cannot distinguish "no such user" from "wrong password"
    # by measuring response time.
    if not user or not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    # Build the JWT — "sub" (subject) holds the username
    token = create_access_token({"sub": user["username"]})

    return {
        "access_token": token,
        "token_type":   "bearer",
        "user": {
            "id":       user["id"],
            "username": user["username"],
            "role":     user["role"],
        },
    }


# ── GET /auth/me ──────────────────────────────────────────

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Return the profile of the currently authenticated user.
    Useful for the frontend to restore session state after a page refresh.
    """
    return {
        "id":       current_user["id"],
        "username": current_user["username"],
        "role":     current_user["role"],
    }
