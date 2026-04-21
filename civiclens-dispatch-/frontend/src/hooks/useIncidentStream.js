// frontend/src/hooks/useIncidentStream.js
// Custom hook that maintains a WebSocket connection to the backend and
// calls a callback whenever an incident event arrives.
//
// Day 71: WebSockets for live incident updates
//
// Features:
//   - Opens ws://localhost:8000/ws/incidents on mount
//   - Calls onMessage(parsedEvent) for every incoming message
//   - Exponential backoff reconnect: 1s → 2s → 4s → ... → 30s max
//   - Resets backoff to 1s on a successful connection
//   - Cleans up the socket and any pending timers on unmount
//
// Usage in App.jsx:
//   const { connected } = useIncidentStream((event) => {
//     if (event.event === 'incident_created') { ... }
//     if (event.event === 'incident_updated') { ... }
//   })

import { useState, useEffect, useRef, useCallback } from 'react'

// WebSocket URL — points at the FastAPI ws endpoint
// VITE_WS_URL can be set in .env for production deployments
const WS_URL =
  (import.meta.env.VITE_WS_URL || 'ws://localhost:8000') + '/ws/incidents'

// ── CONSTANTS ─────────────────────────────────────────────
const INITIAL_RETRY_MS = 1000    // 1 second on first retry
const MAX_RETRY_MS     = 30000   // cap at 30 seconds


export default function useIncidentStream(onMessage) {

  // Whether the WebSocket is currently in the OPEN state
  const [connected, setConnected] = useState(false)

  // Refs avoid stale closures and don't cause re-renders on change
  const wsRef          = useRef(null)          // current WebSocket instance
  const retryDelayRef  = useRef(INITIAL_RETRY_MS)  // current backoff delay
  const reconnectTimer = useRef(null)          // setTimeout handle
  const isMounted      = useRef(true)          // false after unmount
  const onMessageRef   = useRef(onMessage)     // always points to latest callback

  // Keep onMessageRef current on every render (pattern from useAutoRefresh)
  useEffect(() => { onMessageRef.current = onMessage })

  // ── CONNECT ────────────────────────────────────────────
  // Wrapped in useCallback for a stable reference so the cleanup
  // useEffect can list it as a dependency without infinite looping.
  const connect = useCallback(() => {
    // Don't attempt a new connection after the component unmounted
    if (!isMounted.current) return

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      if (!isMounted.current) { ws.close(); return }
      setConnected(true)
      // Reset backoff — a successful connection means the server is healthy
      retryDelayRef.current = INITIAL_RETRY_MS
    }

    ws.onmessage = (event) => {
      // Parse the JSON payload and forward to the caller
      try {
        const data = JSON.parse(event.data)
        onMessageRef.current?.(data)
      } catch {
        // Ignore malformed messages — don't crash the hook
      }
    }

    ws.onclose = () => {
      if (!isMounted.current) return
      setConnected(false)

      // Schedule a reconnect with exponential backoff
      const delay = retryDelayRef.current
      // Double the delay for the next attempt, capped at MAX_RETRY_MS
      retryDelayRef.current = Math.min(delay * 2, MAX_RETRY_MS)
      reconnectTimer.current = setTimeout(connect, delay)
    }

    ws.onerror = () => {
      // onerror always fires before onclose; closing here triggers onclose
      // which schedules the reconnect — no duplicate logic needed
      ws.close()
    }
  }, []) // stable: no external dependencies; retryDelayRef is a ref


  // ── LIFECYCLE ──────────────────────────────────────────
  useEffect(() => {
    isMounted.current = true
    connect()

    // Cleanup: close the socket and cancel any pending reconnect timer
    return () => {
      isMounted.current = false
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])


  return { connected }
}
