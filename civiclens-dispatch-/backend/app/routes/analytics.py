# backend/app/routes/analytics.py
# Analytics endpoints providing aggregate statistics about incidents.
# Registered under prefix /incidents/analytics.
#
# Endpoints:
#   GET /incidents/analytics/summary         — KPI cards + chart data
#   GET /incidents/analytics/timeseries      — daily counts with zero-fill
#   GET /incidents/analytics/risk-distribution — histogram buckets
#
# All aggregation happens in SQL (COUNT, GROUP BY, CASE WHEN).
# No full incident rows are shipped to the frontend.
#
# Day 55: Original /analytics/summary endpoint
# Day 70: Moved to /incidents/analytics prefix; added timeseries and
#          risk-distribution; updated summary to return chart-friendly arrays

from fastapi import APIRouter, Query
from sqlalchemy import func, case, select
from datetime import datetime, timezone, timedelta

from app.db.database import database
from app.db.models import incidents
from app.logging_config import get_logger

logger = get_logger(__name__)


# ========================================
# ROUTER SETUP
# ========================================

# Prefix /incidents/analytics puts all three endpoints under that path.
# FastAPI resolves this AFTER the incidents router, so /{incident_id}
# (which expects an int) will never match "analytics".
router = APIRouter(
    prefix="/incidents/analytics",
    tags=["Analytics"],
)


# ============================================================
# GET /incidents/analytics/summary
# ============================================================

@router.get("/summary")
async def get_analytics_summary():
    """
    Aggregate statistics used by the analytics dashboard.

    Returns:
        total_incidents   — total row count
        average_risk_score — mean of non-null risk_score (0.0–1.0)
        high_severity_count — incidents where severity == 'high'
        most_common_type  — incident_type with the highest count
        by_type           — list of {name, count} for each incident type
        by_severity       — list of {name, count} for each severity level

    by_type and by_severity are formatted as recharts-compatible arrays.
    """

    logger.info("Generating analytics summary")

    # ── TOTAL COUNT ───────────────────────────────────────
    # COUNT(*) over the full table — fastest aggregate
    total_query = select(func.count()).select_from(incidents)
    total = await database.fetch_val(total_query)

    # ── AVERAGE RISK SCORE ────────────────────────────────
    # Only include incidents that have been AI-processed (risk_score IS NOT NULL)
    avg_risk_query = select(func.avg(incidents.c.risk_score)).where(
        incidents.c.risk_score.isnot(None)
    )
    avg_risk = await database.fetch_val(avg_risk_query)
    # Round to 4 decimal places; default to 0.0 if no AI-processed incidents exist
    avg_risk = round(float(avg_risk), 4) if avg_risk else 0.0

    # ── HIGH SEVERITY COUNT ───────────────────────────────
    # Exact-match filter — this feeds the "High Severity" KPI card
    high_sev_query = select(func.count()).select_from(incidents).where(
        incidents.c.severity == "high"
    )
    high_severity_count = await database.fetch_val(high_sev_query)

    # ── MOST COMMON INCIDENT TYPE ─────────────────────────
    # GROUP BY incident_type, ORDER BY count DESC, LIMIT 1
    # NULL types are excluded (unprocessed incidents have no type yet)
    top_type_query = (
        select(incidents.c.incident_type, func.count().label("cnt"))
        .where(incidents.c.incident_type.isnot(None))
        .group_by(incidents.c.incident_type)
        .order_by(func.count().desc())
        .limit(1)
    )
    top_type_row = await database.fetch_one(top_type_query)
    most_common_type = top_type_row["incident_type"] if top_type_row else "N/A"

    # ── COUNT BY TYPE (array for recharts BarChart) ───────
    # Returns rows ordered by count descending for a natural bar chart order
    type_query = (
        select(
            incidents.c.incident_type.label("name"),
            func.count().label("count"),
        )
        .group_by(incidents.c.incident_type)
        .order_by(func.count().desc())
    )
    type_rows = await database.fetch_all(type_query)
    # Normalize NULL type to "unclassified" so the chart always has a label
    by_type = [
        {"name": row["name"] or "unclassified", "count": row["count"]}
        for row in type_rows
    ]

    # ── COUNT BY SEVERITY (array for recharts BarChart) ───
    severity_query = (
        select(
            incidents.c.severity.label("name"),
            func.count().label("count"),
        )
        .group_by(incidents.c.severity)
        .order_by(func.count().desc())
    )
    sev_rows = await database.fetch_all(severity_query)
    by_severity = [
        {"name": row["name"] or "unclassified", "count": row["count"]}
        for row in sev_rows
    ]

    logger.info(
        "Analytics summary: %d total, avg_risk=%.2f, high_sev=%d, top_type=%s",
        total, avg_risk, high_severity_count, most_common_type,
    )

    return {
        "total_incidents": total,
        "average_risk_score": avg_risk,
        "high_severity_count": high_severity_count,
        "most_common_type": most_common_type,
        "by_type": by_type,
        "by_severity": by_severity,
    }


# ============================================================
# GET /incidents/analytics/timeseries?days=30
# ============================================================

@router.get("/timeseries")
async def get_timeseries(
    days: int = Query(default=30, ge=1, le=365, description="Number of past days to include"),
):
    """
    Daily incident counts for the last N days.

    Zero-fills days with no incidents so the chart never has gaps.
    The date column uses SQLite's strftime() which is UTC-aware because
    created_at values are stored as UTC ISO timestamps.

    Returns:
        list of {date: "YYYY-MM-DD", count: int}, oldest date first
    """

    # Calculate the cutoff — only incidents on or after this date are counted
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # ── SQL: group incidents by calendar day ──────────────
    # func.strftime('%Y-%m-%d', ...) is SQLite-specific.
    # For PostgreSQL, the equivalent is func.date_trunc('day', ...).
    # This app targets SQLite for development; swap the expression if migrating.
    date_expr = func.strftime("%Y-%m-%d", incidents.c.created_at)
    ts_query = (
        select(
            date_expr.label("date"),
            func.count().label("count"),
        )
        .where(incidents.c.created_at >= cutoff)
        .group_by(date_expr)
        .order_by(date_expr.asc())
    )
    rows = await database.fetch_all(ts_query)

    # Convert DB results to a dict for O(1) date lookup
    db_counts = {row["date"]: row["count"] for row in rows}

    # ── ZERO-FILL ─────────────────────────────────────────
    # Generate every calendar day in the range, even if no incidents occurred.
    # Without this, recharts would draw a straight line between non-adjacent days.
    result = []
    for offset in range(days - 1, -1, -1):
        # offset=days-1 → oldest day, offset=0 → today
        day_str = (datetime.now(timezone.utc) - timedelta(days=offset)).strftime("%Y-%m-%d")
        result.append({"date": day_str, "count": db_counts.get(day_str, 0)})

    return result


# ============================================================
# GET /incidents/analytics/risk-distribution
# ============================================================

@router.get("/risk-distribution")
async def get_risk_distribution():
    """
    Histogram of incident risk scores grouped into five 20-point buckets.

    risk_score is stored as 0.0–1.0 (float); buckets are named 0-20,
    20-40, 40-60, 60-80, 80-100 to reflect the percentage interpretation
    shown in the UI.

    Only AI-processed incidents (risk_score IS NOT NULL) are included.
    All five buckets are always returned, even if some have count=0.

    Returns:
        list of {bucket: str, count: int}
    """

    # ── SQL: CASE WHEN bucketing ──────────────────────────
    # CASE evaluates conditions top-to-bottom, stops at first match.
    # Thresholds correspond to 0%, 20%, 40%, 60%, 80%, 100%.
    bucket_expr = case(
        (incidents.c.risk_score < 0.2, "0-20"),
        (incidents.c.risk_score < 0.4, "20-40"),
        (incidents.c.risk_score < 0.6, "40-60"),
        (incidents.c.risk_score < 0.8, "60-80"),
        else_="80-100",
    )
    dist_query = (
        select(
            bucket_expr.label("bucket"),
            func.count().label("count"),
        )
        .where(incidents.c.risk_score.isnot(None))
        .group_by(bucket_expr)
    )
    rows = await database.fetch_all(dist_query)

    # Convert to dict for easy lookup
    db_buckets = {row["bucket"]: row["count"] for row in rows}

    # ── ZERO-FILL ─────────────────────────────────────────
    # Always return all five buckets in ascending order so the histogram
    # labels are stable even when some buckets are empty
    all_buckets = ["0-20", "20-40", "40-60", "60-80", "80-100"]
    return [
        {"bucket": b, "count": db_buckets.get(b, 0)}
        for b in all_buckets
    ]
