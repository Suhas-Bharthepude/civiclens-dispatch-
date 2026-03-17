// frontend/src/hooks/useToast.js
// Custom React hook for managing toast notifications
// Provides functions to show/hide toasts from any component

// Import useState
import { useState } from 'react'


// ========================================
// USE TOAST HOOK
// ========================================

// Custom hook that manages toast notifications
// Returns object with:
//   - toasts: Array of current toasts
//   - showToast: Function to show new toast
//   - removeToast: Function to remove toast
function useToast() {
  
  // ========================================
  // STATE - Array of Toasts
  // ========================================
  
  // State: array of toast objects
  // Each toast has: { id, message, type, duration }
  const [toasts, setToasts] = useState([])
  
  
  // ========================================
  // SHOW TOAST FUNCTION
  // ========================================
  
  // Function to add a new toast
  // Parameters:
  //   - message: Text to display
  //   - type: 'success', 'error', 'warning', or 'info'
  //   - duration: How long to show (milliseconds)
  function showToast(message, type = 'info', duration = 5000) {
    // Create unique ID for this toast
    // Use timestamp + random number for uniqueness
    // This helps React track which toast is which
    const id = Date.now() + Math.random();
    
    // Create toast object
    const newToast = {
      id,           // Unique identifier
      message,      // Text to display
      type,         // Type (success/error/etc.)
      duration      // How long to show
    };
    
    // Add new toast to array
    // Use functional update to ensure we have latest state
    setToasts(prevToasts => [...prevToasts, newToast]);
    
    // Log for debugging
    console.log('Toast shown:', newToast);
    
    // Return the toast id (in case caller wants to remove it manually)
    return id;
  }
  
  
  // ========================================
  // REMOVE TOAST FUNCTION
  // ========================================
  
  // Function to remove a toast by ID
  function removeToast(id) {
    // Filter out the toast with matching id
    // .filter() creates new array without the removed item
    setToasts(prevToasts => 
      prevToasts.filter(toast => toast.id !== id)
    );
    
    // Log for debugging
    console.log('Toast removed:', id);
  }
  
  
  // ========================================
  // RETURN API
  // ========================================
  
  // Return object with toasts array and functions
  // Components can destructure: const { showToast, toasts } = useToast()
  return {
    toasts,        // Current array of toasts
    showToast,     // Function to show new toast
    removeToast    // Function to remove toast
  }
}

export default useToast