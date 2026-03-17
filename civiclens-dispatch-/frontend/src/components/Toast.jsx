// frontend/src/components/Toast.jsx
// Toast notification component for temporary user feedback messages
// Appears in corner, auto-dismisses after timeout

// Import React hooks
import { useEffect } from 'react'

// Import CSS
import './Toast.css'


// ========================================
// TOAST COMPONENT
// ========================================

// Toast notification component
// Props:
//   - message: Text to display
//   - type: 'success', 'error', 'warning', or 'info'
//   - duration: How long to show (milliseconds), default 5000 (5 seconds)
//   - onClose: Callback when toast closes
function Toast({ message, type = 'info', duration = 5000, onClose }) {
  
  // ========================================
  // AUTO-DISMISS TIMER
  // ========================================
  
  // useEffect to set timer for auto-dismissing toast
  useEffect(() => {
    // If onClose callback provided and duration is set
    if (onClose && duration) {
      // Set timeout to call onClose after duration
      // setTimeout returns a timer ID
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      
      // Cleanup function - cancels timer if component unmounts
      // This prevents calling onClose on unmounted component
      return () => {
        clearTimeout(timer);
      };
    }
    
    // Re-run if these values change
  }, [duration, onClose]);
  
  
  // ========================================
  // GET ICON FOR TOAST TYPE
  // ========================================
  
  // Returns emoji icon based on toast type
  function getIcon() {
    switch (type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
      default:
        return 'ℹ️';
    }
  }
  
  
  // ========================================
  // RENDER TOAST
  // ========================================
  
  return (
    // Main toast container
    // CSS class varies by type: toast-success, toast-error, etc.
    // This allows different colors for different types
    <div className={`toast toast-${type}`}>
      
      {/* Icon for visual quick identification */}
      <span className="toast-icon">
        {getIcon()}
      </span>
      
      {/* Message content */}
      <span className="toast-message">
        {message}
      </span>
      
      {/* Close button (X) */}
      {/* Allows manual dismissal before auto-timeout */}
      {onClose && (
        <button 
          className="toast-close"
          onClick={onClose}
          aria-label="Close notification"
        >
          ×
        </button>
      )}
      
    </div>
  )
}

export default Toast