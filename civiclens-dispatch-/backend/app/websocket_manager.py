# backend/app/websocket_manager.py
# Singleton WebSocket connection manager for broadcasting incident events.
#
# Day 71: WebSockets for live incident updates
#
# ConnectionManager tracks every open browser WebSocket connection.
# After a new incident is created (routes/incidents.py) or the AI
# pipeline finishes (services/incident_processor.py), the caller
# does `await manager.broadcast({...})` to push the event to all
# connected dashboards instantly.
#
# Designed to be safe in broadcast: if a connection is broken,
# we remove it silently instead of crashing the caller.

from fastapi import WebSocket
import json


class ConnectionManager:
    """
    Tracks active WebSocket connections and broadcasts JSON messages to all of them.

    One global instance (`manager`) is created at the bottom of this file.
    Import and use that instance everywhere — do not create additional instances.
    """

    def __init__(self):
        # List of currently open WebSocket connections
        # We use a plain list; for very high concurrency a set would be faster,
        # but WebSocket objects are not hashable so list.remove() is the way.
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept the handshake and register the connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a closed or errored connection from the list."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        """
        Send a JSON message to every connected client.

        Dead connections (closed browser tabs, network drops) are detected
        when send_json raises and are removed so the list stays clean.
        This method never raises — a broadcast failure must not crash the
        request handler or AI pipeline that called it.
        """
        # Collect connections that fail so we can remove them after the loop
        # (mutating the list while iterating over it is undefined behaviour)
        dead: list[WebSocket] = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection is broken — mark it for removal
                dead.append(connection)

        # Clean up dead connections outside the iteration loop
        for conn in dead:
            self.disconnect(conn)


# ── GLOBAL SINGLETON ──────────────────────────────────────
# Import this object everywhere; one shared state across the process.
manager = ConnectionManager()
