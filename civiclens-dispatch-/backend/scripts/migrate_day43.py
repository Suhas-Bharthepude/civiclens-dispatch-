# backend/scripts/migrate_day43.py
#
# One-time data migration script for Day 43.
# Fixes two issues in existing database records:
#
#   1. created_at is NULL for all existing incidents
#      → Set to a sensible default (current time)
#
#   2. status is NULL for all existing incidents
#      → Set to "pending" (the correct default)
#
# Run this ONCE:
#   cd ~/Desktop/CivicLensDispatch/civiclens-dispatch-/backend
#   python3 scripts/migrate_day43.py
#
# It's safe to run multiple times — it only updates NULL values.

# sqlite3 is Python's built-in SQLite library
import sqlite3

# datetime for generating timestamps
from datetime import datetime

# os for path handling
import os


def run_migration():
    """
    Run the Day 43 database migration.
    Updates NULL created_at and status fields on existing incidents.
    """

    print()
    print("=" * 50)
    print("  Day 43 Database Migration")
    print("=" * 50)
    print()

    # Path to the SQLite database file
    # Running from backend/ directory
    db_path = "test.db"

    # Verify the database file exists
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("   Make sure you're running from the backend/ directory")
        return

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ── STEP 1: Count affected rows ───────────────────────
    # See how many incidents need updating before we change anything
    cursor.execute("SELECT COUNT(*) FROM incidents WHERE status IS NULL")
    null_status_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incidents WHERE created_at IS NULL")
    null_created_at_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incidents")
    total_count = cursor.fetchone()[0]

    print(f"  Total incidents: {total_count}")
    print(f"  NULL status:     {null_status_count}")
    print(f"  NULL created_at: {null_created_at_count}")
    print()

    # ── STEP 2: Fix NULL status ───────────────────────────
    # All incidents without a status should be "pending"
    # (the default state — not yet acknowledged by dispatcher)
    if null_status_count > 0:
        cursor.execute("""
            UPDATE incidents
            SET status = 'pending'
            WHERE status IS NULL
        """)
        print(f"  ✅ Set {null_status_count} incidents to status='pending'")
    else:
        print("  ✓  All incidents already have a status")

    # ── STEP 3: Fix NULL created_at ───────────────────────
    # Backfill timestamps for incidents that don't have one.
    # We use the current time as a placeholder — not ideal but better than NULL.
    # Real incidents going forward will have proper timestamps.
    if null_created_at_count > 0:
        # Generate a timestamp string in SQLite format
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            UPDATE incidents
            SET created_at = ?
            WHERE created_at IS NULL
        """, (now,))
        print(f"  ✅ Set {null_created_at_count} incidents to created_at='{now}'")
    else:
        print("  ✓  All incidents already have a created_at timestamp")

    # ── STEP 4: Commit and verify ─────────────────────────
    # commit() saves all changes permanently
    conn.commit()

    # Verify the changes took effect
    cursor.execute("SELECT COUNT(*) FROM incidents WHERE status IS NULL")
    remaining_null_status = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incidents WHERE created_at IS NULL")
    remaining_null_created_at = cursor.fetchone()[0]

    print()
    if remaining_null_status == 0 and remaining_null_created_at == 0:
        print("  ✅ Migration complete — no more NULL values")
    else:
        print(f"  ⚠️  Still {remaining_null_status} NULL status, "
              f"{remaining_null_created_at} NULL created_at")

    # Close the database connection
    conn.close()

    print()
    print("  Migration finished!")
    print()


# Run the migration when this script is executed directly
if __name__ == "__main__":
    run_migration()