// frontend/src/hooks/useDebounce.js
//
// A custom React hook that delays updating a value until the user
// has stopped changing it for a specified amount of time.
//
// This is called "debouncing" — it prevents a function from being
// called too many times in rapid succession.
//
// Primary use case: search inputs.
// Without debouncing, typing "oak street" (9 characters) would trigger
// 9 API calls. With 400ms debouncing, it triggers 1 API call after
// the user stops typing.
//
// Usage:
//   const debouncedValue = useDebounce(rawValue, 400)
//
//   rawValue      - the value that changes rapidly (e.g., search input state)
//   400           - milliseconds to wait after last change
//   debouncedValue - the delayed version that only updates after the pause
//
// Example:
//   const [search, setSearch] = useState('')
//   const debouncedSearch = useDebounce(search, 400)
//
//   // debouncedSearch only updates 400ms after the user stops typing
//   useEffect(() => {
//     fetchResults(debouncedSearch)
//   }, [debouncedSearch])

// useState and useEffect are the two hooks we need from React
import { useState, useEffect } from 'react'

// ============================================================
// THE HOOK
// ============================================================
// Parameters:
//   value    - the rapidly-changing value to debounce (any type)
//   delayMs  - how long to wait (in milliseconds) before updating
//              400ms is a good default for search inputs —
//              fast enough to feel responsive, slow enough to avoid spam
//
// Returns:
//   debouncedValue - the delayed version of value
//                   only changes after delayMs of no changes to value
function useDebounce(value, delayMs) {

  // debouncedValue: the "stable" version of value that we return
  // It starts as the initial value and only updates after the delay
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    // Every time 'value' changes, we set a timer to update debouncedValue
    // after delayMs milliseconds.
    //
    // setTimeout returns an ID number we can use to cancel the timer later.
    // The callback function runs after delayMs ms if not cancelled.
    const timerId = setTimeout(() => {
      // delayMs have passed without value changing again
      // Update debouncedValue to the latest value
      setDebouncedValue(value)
    }, delayMs)

    // CLEANUP FUNCTION — React calls this when:
    //   1. value changes again before the timer fires
    //   2. The component using this hook unmounts
    //
    // clearTimeout cancels the pending timer.
    // This is what creates the debounce effect:
    //   - User types "o" → timer starts (400ms)
    //   - User types "a" → CANCEL old timer, start new timer (400ms)
    //   - User types "k" → CANCEL old timer, start new timer (400ms)
    //   - User stops → timer fires after 400ms → debouncedValue = "oak"
    //
    // Without this cleanup, every keystroke would trigger a separate update.
    return () => {
      clearTimeout(timerId)
    }

  }, [value, delayMs])
  // ^ Re-run this effect whenever value or delayMs changes

  // Return the debounced (delayed) value
  // The component using this hook will see updates only after the pause
  return debouncedValue
}

// Export so components can import and use it
export default useDebounce