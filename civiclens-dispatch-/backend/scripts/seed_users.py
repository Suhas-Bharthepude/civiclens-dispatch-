# backend/scripts/seed_users.py
# Creates the default admin and dispatcher accounts for development.
#
# Day 72: Auth with admin and dispatcher roles
#
# ⚠️  DEVELOPMENT ONLY — do NOT run this in production with these passwords.
#    Change passwords immediately if you use this on a shared server.
#
# Usage (from the repo root, with the venv active):
#   cd backend
#   PYTHONPATH=. python scripts/seed_users.py
#
# The script is idempotent — running it twice does not create duplicates.

import asyncio
import sys
from datetime import datetime, timezone

# Add the backend directory to sys.path so app imports resolve
sys.path.insert(0, ".")

from databases import Database
from app.config import settings
from app.db.models import metadata, users
from app.auth import hash_password
from sqlalchemy import create_engine


# ── SEED DATA ─────────────────────────────────────────────
# Credentials are intentionally obvious — change before any real deployment
SEED_USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "role":     "admin",
    },
    {
        "username": "dispatcher",
        "password": "dispatch123",
        "role":     "dispatcher",
    },
]


async def seed():
    """Connect to the database and upsert the seed accounts."""

    print("=" * 60)
    print("⚠️   DEVELOPMENT SEED SCRIPT — NOT FOR PRODUCTION USE")
    print("⚠️   These passwords are public knowledge. Change them.")
    print("=" * 60)

    # ── ENSURE TABLES EXIST ───────────────────────────────
    # create_all is idempotent — safe to call even if tables already exist
    sync_url = settings.SYNC_DATABASE_URL
    engine = create_engine(
        sync_url,
        connect_args={"check_same_thread": False} if "sqlite" in sync_url else {},
    )
    metadata.create_all(engine)
    engine.dispose()
    print("\n✅ Tables verified / created")

    # ── CONNECT ASYNC DATABASE ────────────────────────────
    db = Database(settings.DATABASE_URL)
    await db.connect()

    try:
        for seed_user in SEED_USERS:
            # Check if the user already exists
            existing = await db.fetch_one(
                users.select().where(users.c.username == seed_user["username"])
            )

            if existing:
                # Idempotent — don't overwrite existing accounts
                print(f"   ℹ️  '{seed_user['username']}' already exists — skipping")
                continue

            # Hash the password before inserting
            hashed = hash_password(seed_user["password"])

            await db.execute(
                users.insert().values(
                    username=seed_user["username"],
                    hashed_password=hashed,
                    role=seed_user["role"],
                    created_at=datetime.now(timezone.utc),
                )
            )
            print(
                f"   ✅ Created '{seed_user['username']}'"
                f" (role={seed_user['role']},"
                f" password={seed_user['password']})"
            )

        print("\n🔑 Seed complete. Login credentials:")
        print("   admin      / admin123    → role: admin")
        print("   dispatcher / dispatch123 → role: dispatcher")
        print("\n⚠️  Change these passwords before exposing to a network!")

    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(seed())
