# backend/app/auth.py
# Authentication utilities for CivicLens Dispatch.
#
# Day 72: Auth with admin and dispatcher roles
#
# Provides:
#   hash_password(plain)           — bcrypt hash a password
#   verify_password(plain, hashed) — check a password against its hash
#   create_access_token(data)      — sign a JWT with SECRET_KEY
#   get_current_user(token)        — FastAPI dependency: decode JWT → user dict
#   require_role(role)             — dependency factory: enforces a specific role
#
# JWT payload shape: {"sub": username, "exp": expiry_timestamp}
#
# SECRET_KEY is read from settings (config.py).
# It must be set in .env for production — the default dev value is
# intentionally obvious so no one accidentally ships it.

from datetime import datetime, timedelta, timezone

# FastAPI dependency injection and HTTP exceptions
from fastapi import Depends, HTTPException
# OAuth2PasswordBearer extracts the Bearer token from the Authorization header
from fastapi.security import OAuth2PasswordBearer

# passlib handles bcrypt hashing — never roll your own crypto
from passlib.context import CryptContext

# python-jose handles JWT encoding/decoding
from jose import JWTError, jwt

from app.config import settings
from app.db.database import database
from app.db.models import users


# ── PASSWORD HASHING ──────────────────────────────────────
# CryptContext configures which algorithm to use.
# bcrypt is the industry standard for password storage.
# "deprecated=auto" means older hashes are automatically re-hashed on
# next login if a stronger algorithm is configured in the future.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    return pwd_context.verify(plain, hashed)


# ── JWT SETTINGS ──────────────────────────────────────────
ALGORITHM = "HS256"
# Token expires after 8 hours — long enough for a work shift without
# requiring re-login, short enough to limit exposure if a token leaks.
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Sign and return a JWT.

    `data` is copied and an "exp" claim is added.
    The token is signed with settings.SECRET_KEY using HS256.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # "exp" is a standard JWT claim — jose validates it automatically on decode
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


# ── TOKEN EXTRACTION ──────────────────────────────────────
# OAuth2PasswordBearer reads the Authorization: Bearer <token> header.
# tokenUrl is the URL shown in the auto-generated /docs login form.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    FastAPI dependency: decode the JWT and return the user dict from the DB.

    Raises HTTP 401 if:
      - The Authorization header is missing (oauth2_scheme handles this)
      - The token is expired or has an invalid signature
      - The username in the token doesn't exist in the database
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode and verify the JWT — raises JWTError if signature or expiry fails
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        # "sub" (subject) holds the username we stored at login time
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Verify the user still exists in the database (handles deleted accounts)
    query = users.select().where(users.c.username == username)
    user = await database.fetch_one(query)
    if user is None:
        raise credentials_exception

    # Return as a plain dict so callers don't need to import the Row type
    return dict(user)


def require_role(role: str):
    """
    Dependency factory that checks the current user has the required role.

    Usage:
        @router.delete("/{id}", dependencies=[Depends(require_role("admin"))])
        async def delete_incident(incident_id: int):
            ...

    Raises HTTP 403 if the authenticated user's role doesn't match.
    HTTP 401 is raised first (by get_current_user) if the token is invalid.
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] != role:
            raise HTTPException(
                status_code=403,
                detail=f"This action requires the '{role}' role",
            )
        return current_user
    return role_checker
