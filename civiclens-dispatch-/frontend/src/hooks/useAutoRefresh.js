// frontend/src/hooks/useAutoRefresh.js
//
// A custom React hook that automatically calls a function on a timer.
// It handles the interval setup, cleanup, refresh state, and
// "last updated" timestamp — so components don't need to manage
// any of that themselves.
//
// Usage:
//   const { isRefreshing, lastUpdated, triggerRefresh } = useAutoRefresh(
//     myFetchFunction,  // function to call on each refresh
//     30000             // interval in milliseconds (30 seconds)
//   )
//
// What it returns:
//   isRefreshing  - true while a background refresh is in progress
//   lastUpdated   - Date object of the last successful refresh (or null)
//   triggerRefresh - call this to refresh immediately (e.g., a "Refresh Now" button)

// Import hooks from React
// useState: stores isRefreshing, lastUpdated
// useEffect: sets up and tears down the interval
// useRef: stores a stable reference to the callback function
// useCallback: memoizes the refresh function so it doesn't recreate every render
import { useState, useEffect, useRef, useCallback } from 'react'

// ============================================================
// THE HOOK
// ============================================================
// Parameters:
//   callback    - the async function to call on each refresh
//                 (e.g., the fetchIncidents function from IncidentsList)
//   intervalMs  - how often to refresh in milliseconds
//                 (e.g., 30000 = every 30 seconds)
//   enabled     - optional boolean to pause/resume the interval (default: true)
function useAutoRefresh(callback, intervalMs, enabled = true) {

  // isRefreshing: true while a background refresh request is in flight
  // Used by the component to show a small "updating..." indicator
  // NOT the same as the initial loading state — this is for quiet background updates
  const [isRefreshing, setIsRefreshing] = useState(false)

  // lastUpdated: a Date object recording when the last successful refresh completed
  // null means no refresh has completed yet (initial state)
  // The component uses this to show "Updated 14 seconds ago"
  const [lastUpdated, setLastUpdated] = useState(null)

  // refreshError: stores an error message if the last refresh failed
  // null means the last refresh was successful (or hasn't run yet)
  const [refreshError, setRefreshError] = useState(null)

  // callbackRef: stores a reference to the latest version of the callback function
  // We use useRef instead of including callback in useEffect's dependency array
  // because we don't want to restart the interval every time the callback changes.
  // useRef gives us a mutable container that persists across renders without
  // causing re-renders when it changes.
  const callbackRef = useRef(callback)

  // Keep callbackRef.current updated whenever callback changes
  // This runs on every render, ensuring we always have the latest callback
  // without recreating the interval
  useEffect(() => {
    callbackRef.current = callback
  })

  // ── THE REFRESH FUNCTION ──────────────────────────────
  // This is the function that actually calls the callback.
  // We wrap it in useCallback so it has a stable identity —
  // meaning it won't be recreated on every render.
  // This is important because we pass it to the interval
  // and also return it for "Refresh Now" buttons.
  //
  // isBackground: if true, this is a quiet background poll
  //               if false, this was triggered manually (show louder feedback)
  const doRefresh = useCallback(async (isBackground = true) => {

    // Don't start a new refresh if one is already running
    // This prevents overlapping requests if the interval fires while
    // a previous request is still in flight (e.g., slow network)
    if (isRefreshing) return

    // Mark that a refresh is now in progress
    setIsRefreshing(true)

    // Clear any previous error — we're trying again
    setRefreshError(null)

    try {
      // Call the actual fetch function (e.g., fetchIncidents)
      // callbackRef.current always points to the latest version
      await callbackRef.current()

      // Success — record the current time as the last successful update
      setLastUpdated(new Date())

    } catch (err) {
      // The fetch failed (network error, server down, etc.)
      // Store the error message so the component can show it
      setRefreshError(err.message || 'Refresh failed')

      // Note: we do NOT clear lastUpdated here —
      // the last successful time is still valid information

    } finally {
      // Always clear the refreshing state, whether success or failure
      // 'finally' runs even if the catch block threw an error
      setIsRefreshing(false)
    }

  }, [isRefreshing]) // isRefreshing is the only dependency

  // ── SET UP THE INTERVAL ───────────────────────────────
  // This effect runs when the component mounts and when enabled/intervalMs change.
  // It sets up a timer that calls doRefresh on a fixed schedule.
  useEffect(() => {

    // If polling is disabled (e.g., during tests), don't set up the interval
    if (!enabled) return

    // setInterval schedules doRefresh to run every intervalMs milliseconds
    // It returns an ID number we use to cancel the interval later
    const intervalId = setInterval(() => {
      // Pass isBackground=true so the component knows this is a quiet poll
      doRefresh(true)
    }, intervalMs)

    // CLEANUP FUNCTION — React calls this when:
    //   1. The component unmounts (disappears from the page)
    //   2. The effect re-runs because enabled or intervalMs changed
    // Without this, the interval would keep firing forever even after the
    // component is gone, causing memory leaks and errors
    return () => {
      clearInterval(intervalId)
    }

  }, [enabled, intervalMs, doRefresh])
  // ^ Dependencies: re-run this effect if any of these change

  // ── RETURN VALUES ─────────────────────────────────────
  // Return everything the component needs to:
  //   - Show a refreshing indicator (isRefreshing)
  //   - Show last updated time (lastUpdated)
  //   - Show/handle errors (refreshError)
  //   - Let user manually trigger a refresh (triggerRefresh)
  return {
    // true while a background refresh is in progress
    isRefreshing,

    // Date object of last successful refresh, or null
    lastUpdated,

    // Error message string if last refresh failed, or null
    refreshError,

    // Call this to immediately trigger a refresh (e.g., from a "Refresh Now" button)
    // We bind isBackground=false so the component knows it was manual
    triggerRefresh: () => doRefresh(false),
  }
}

export default useAutoRefresh