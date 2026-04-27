# backend/app/routes/ws_routes.py
# WebSocket endpoint for real-time incident updates.
#
# Day 71: WebSockets for live incident updates
#
# Endpoint: GET /ws/incidents  (upgrades to WebSocket)
#
# Clients connect once on page load. When any incident is created or
# its AI fields are updated, the backend pushes a JSON event over the
# open connection instead of the client polling every 30 seconds.
#
# The endpoint keeps the connection alive by waiting for client messages.
# Browsers don't send data here — they just listen — but the receive loop
# is required so FastAPI doesn't drop the connection immediately.

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_manager import manager


# ── ROUTER ────────────────────────────────────────────────
# No prefix — the WebSocket lives at /ws/incidents, not under /incidents
router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/incidents")
async def websocket_incidents(websocket: WebSocket):
    """
    WebSocket endpoint that streams incident events to connected browsers.

    Event shapes sent to clients:
        {"event": "incident_created", "incident": {...full incident dict...}}
        {"event": "incident_updated", "incident": {...full incident dict...}}

    The client sends nothing; we just keep the connection alive until
    the browser tab closes or the user navigates away.
    """

    # Register this connection with the manager — accept() is called inside
    await manager.connect(websocket)

    try:
        # Keep the connection open by waiting for client messages.
        # The loop exits when WebSocketDisconnect is raised (tab closed, etc.)
        while True:
            # receive_text() blocks until the client sends data or disconnects.
            # We don't actually use the data — the client just keeps us alive.
            await websocket.receive_text()

    except WebSocketDisconnect:
        # Normal closure — browser tab closed or user navigated away
        manager.disconnect(websocket)

    except Exception:
        # Unexpected error — still clean up the connection
        manager.disconnect(websocket)
