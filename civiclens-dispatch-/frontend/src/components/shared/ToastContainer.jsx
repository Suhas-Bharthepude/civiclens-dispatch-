// frontend/src/components/ToastContainer.jsx
// Container that manages and displays multiple toast notifications
// Stacks toasts vertically in top-right corner

// Import React
import React from 'react'

// Import Toast component
import Toast from './Toast'

// Import CSS
import './ToastContainer.css'


// ========================================
// TOAST CONTAINER COMPONENT
// ========================================

// Container component that displays multiple toasts
// Props:
//   - toasts: Array of toast objects
//       Each toast object: { id, message, type, duration }
//   - removeToast: Function to remove a toast by id
function ToastContainer({ toasts, removeToast }) {
  
  // If no toasts, don't render anything
  // This prevents empty container from taking up space
  if (!toasts || toasts.length === 0) {
    return null;
  }
  
  // ========================================
  // RENDER TOAST STACK
  // ========================================
  
  return (
    // Fixed container in top-right corner
    <div className="toast-container">
      
      {/* Map over toasts array and render each one */}
      {toasts.map((toast, index) => (
        // Render Toast component for each toast
        // key is required for mapped elements (use unique id)
        // style sets position - each toast stacked below previous
        // index * 80 means: 0px, 80px, 160px, etc. (spacing between toasts)
        <div 
          key={toast.id}
          style={{ top: `${index * 80}px` }}
          className="toast-wrapper"
        >
          <Toast
            message={toast.message}
            type={toast.type}
            duration={toast.duration}
            onClose={() => removeToast(toast.id)}
          />
        </div>
      ))}
      
    </div>
  )
}

export default ToastContainer