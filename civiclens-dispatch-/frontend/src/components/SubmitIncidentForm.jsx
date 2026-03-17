// frontend/src/components/SubmitIncidentForm.jsx
// Form component for citizens to submit new incident reports
// Features: Controlled inputs, validation, file uploads, API integration

// Import React hooks
import { useState } from 'react'

// Import API function to create incidents
import { createIncident } from '../api/client'

// Import CSS
import './SubmitIncidentForm.css'


// ========================================
// SUBMIT INCIDENT FORM COMPONENT
// ========================================

// Component that renders incident submission form
// Props:
//   - onIncidentSubmitted: Callback function to notify parent when incident is created
function SubmitIncidentForm({ onIncidentSubmitted }) {
  
  // ========================================
  // STATE - Form Data
  // ========================================
  
  // State: form field values
  // All inputs are controlled by React state
  // This is a single object containing all form fields
  const [formData, setFormData] = useState({
    source: '',         // Who is reporting (dropdown)
    description: '',    // What happened (textarea)
    location: ''        // Where it happened (text input)
  })
  
  // State: uploaded files (for future Day 31 when we implement actual upload)
  // For now, we'll just track them in state
  const [audioFile, setAudioFile] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  
  // State: form submission status
  // These control what messages to show and whether form is active
  const [submitting, setSubmitting] = useState(false)  // Is form being submitted?
  const [submitSuccess, setSubmitSuccess] = useState(false)  // Was submission successful?
  const [submitError, setSubmitError] = useState(null)  // Error message if failed
  
  
  // ========================================
  // VALIDATION FUNCTION
  // ========================================
  
  // Validate form data before submission
  // Returns true if valid, false if invalid
  // Sets error message if validation fails
  function validateForm() {
    // Clear any existing error first
    setSubmitError(null);
    
    // Check if source is selected
    if (formData.source === '') {
      setSubmitError('Please select a report source');
      return false;
    }
    
    // Check description length (minimum 10 characters)
    if (formData.description.length < 10) {
      setSubmitError('Description must be at least 10 characters');
      return false;
    }
    
    // Check location is not empty
    // .trim() removes whitespace from start and end
    if (formData.location.trim() === '') {
      setSubmitError('Location is required');
      return false;
    }
    
    // All validations passed!
    return true;
  }
  
  
  // ========================================
  // EVENT HANDLERS
  // ========================================
  
  // Handle changes to text inputs, textareas, and selects
  // This function is called whenever any input changes
  function handleInputChange(event) {
    // event.target is the input element that changed
    // Destructure to get name and value
    const { name, value } = event.target;
    
    // Log for debugging
    console.log(`Field "${name}" changed to:`, value);
    
    // Update formData state
    // Use spread operator (...) to copy existing data
    // Then override the specific field that changed
    setFormData({
      ...formData,      // Copy all existing fields (source, description, location)
      [name]: value     // Update the field that changed (dynamic key)
    });
    
    // Example walkthrough:
    // Current formData: { source: 'citizen', description: '', location: '' }
    // User types "F" in description
    // name = "description", value = "F"
    // New formData: { source: 'citizen', description: 'F', location: '' }
  }
  
  // Handle audio file selection
  function handleAudioChange(event) {
    // event.target.files is a FileList object (array-like)
    // [0] gets the first (and only) file selected
    const file = event.target.files[0];
    
    // Update audioFile state with the selected file
    setAudioFile(file);
    
    // Log file details for debugging
    if (file) {
      console.log('Audio file selected:', {
        name: file.name,      // Filename
        size: file.size,      // Size in bytes
        type: file.type       // MIME type (audio/wav, audio/mp3, etc.)
      });
    }
  }
  
  // Handle image file selection
  function handleImageChange(event) {
    // Same as audio - get first file from FileList
    const file = event.target.files[0];
    
    // Update imageFile state
    setImageFile(file);
    
    // Log file details
    if (file) {
      console.log('Image file selected:', {
        name: file.name,
        size: file.size,
        type: file.type       // MIME type (image/jpeg, image/png, etc.)
      });
    }
  }
  
  // Handle form submission
  async function handleSubmit(event) {
    // CRITICAL: Prevent default form submission behavior
    // Without this, the page would reload (old-school HTML form behavior)
    // We want to handle submission with JavaScript instead
    event.preventDefault();
    
    // Log submission attempt
    console.log('Form submitted with data:', formData);
    
    // Validate form data before sending to API
    // If validation fails, stop here
    if (!validateForm()) {
      console.log('Validation failed');
      return;  // Exit function early
    }
    
    // Set submitting state to true
    // This disables the submit button (prevents double submission)
    // Also changes button text to "Submitting..."
    setSubmitting(true);
    
    // Clear any previous error messages
    setSubmitError(null);
    
    // Clear any previous success messages
    setSubmitSuccess(false);
    
    try {
      // Call API to create incident
      // This makes POST request to http://localhost:8000/incidents
      // Sends formData as JSON in request body
      const newIncident = await createIncident(formData);
      
      // Log successful creation
      console.log('Incident created successfully:', newIncident);
      
      // Show success message
      setSubmitSuccess(true);
      
      // Reset form fields to empty
      // This clears the form for the next submission
      setFormData({
        source: '',
        description: '',
        location: ''
      });
      
      // Clear file selections from state
      setAudioFile(null);
      setImageFile(null);
      
      // Reset file input elements (clear the selected file names shown in UI)
      // getElementById finds the input element by its id attribute
      const audioInput = document.getElementById('audio');
      const imageInput = document.getElementById('image');
      
      // Clear the file inputs if they exist
      if (audioInput) audioInput.value = '';
      if (imageInput) imageInput.value = '';
      
      // Notify parent component that incident was submitted
      // Parent will increment refreshTrigger which causes IncidentsList to re-fetch
      if (onIncidentSubmitted) {
        onIncidentSubmitted();
      }
      
      // Hide success message after 5 seconds
      // setTimeout runs a function after a delay (in milliseconds)
      setTimeout(() => {
        setSubmitSuccess(false);
      }, 5000);  // 5000ms = 5 seconds
      
    } catch (error) {
      // If API call fails, catch the error
      console.error('Failed to create incident:', error);
      
      // Show error message to user
      setSubmitError(error.message);
      
    } finally {
      // Always turn off submitting state (whether success or error)
      // finally block runs regardless of try/catch outcome
      setSubmitting(false);
    }
  }
  
  
  // ========================================
  // RETURN JSX
  // ========================================
  
  return (
    // Main container div for the form
    <div className="submit-form-container">
      
      {/* Form header */}
      <h2>📝 Submit New Incident Report</h2>
      
      {/* Form description */}
      <p className="form-description">
        Report an emergency or incident. All fields marked with * are required.
      </p>
      
      {/* ========================================
          SUCCESS MESSAGE
          ======================================== */}
      
      {/* Show success message if submission succeeded */}
      {/* && means: only render if submitSuccess is true */}
      {/* If submitSuccess is false, nothing renders */}
      {submitSuccess && (
        <div className="alert alert-success">
          <strong>✅ Success!</strong> Incident submitted successfully. 
          Dispatchers have been notified and will respond shortly.
        </div>
      )}
      
      {/* ========================================
          ERROR MESSAGE
          ======================================== */}
      
      {/* Show error message if submission failed */}
      {submitError && (
        <div className="alert alert-error">
          <strong>❌ Error!</strong> {submitError}
        </div>
      )}
      
      {/* ========================================
          FORM ELEMENT
          ======================================== */}
      
      {/* The <form> element wraps all inputs */}
      {/* onSubmit is called when form is submitted (user clicks submit or presses Enter) */}
      {/* className for styling from CSS */}
      <form onSubmit={handleSubmit} className="incident-form">
        
        {/* ========================================
            FORM FIELD: Source (Dropdown)
            ======================================== */}
        
        <div className="form-group">
          {/* Label for this field */}
          {/* htmlFor links to input with matching id (accessibility) */}
          <label htmlFor="source">
            Report Source: <span className="required">*</span>
          </label>
          
          {/* Select dropdown */}
          <select
            id="source"
            name="source"
            value={formData.source}
            onChange={handleInputChange}
            required
            className="form-control"
          >
            {/* Placeholder option (empty value) */}
            <option value="">-- Select Source --</option>
            
            {/* Available options */}
            <option value="citizen">Citizen</option>
            <option value="police">Police</option>
            <option value="dispatcher">Dispatcher</option>
            <option value="sensor">Automated Sensor</option>
          </select>
        </div>
        
        {/* ========================================
            FORM FIELD: Description (Textarea)
            ======================================== */}
        
        <div className="form-group">
          <label htmlFor="description">
            Incident Description: <span className="required">*</span>
          </label>
          
          {/* Textarea for multi-line input */}
          {/* rows="5" sets initial height (5 lines) */}
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            rows="5"
            placeholder="Describe what happened in detail..."
            required
            className="form-control"
          />
          
          {/* Character count helper text */}
          {/* Shows current length and warning if too short */}
          <small className="form-hint">
            {formData.description.length} characters
            {/* Show warning if less than 20 characters */}
            {formData.description.length < 20 && ' (minimum 20 recommended)'}
          </small>
        </div>
        
        {/* ========================================
            FORM FIELD: Location (Text Input)
            ======================================== */}
        
        <div className="form-group">
          <label htmlFor="location">
            Location: <span className="required">*</span>
          </label>
          
          {/* Text input for location */}
          {/* type="text" makes it a single-line text field */}
          <input
            type="text"
            id="location"
            name="location"
            value={formData.location}
            onChange={handleInputChange}
            placeholder="123 Main Street, City, State"
            required
            className="form-control"
          />
          
          <small className="form-hint">
            📍 Be as specific as possible (street address, landmarks, intersections)
          </small>
        </div>
        
        {/* ========================================
            FORM FIELD: Audio Upload (Optional)
            ======================================== */}
        
        <div className="form-group">
          <label htmlFor="audio">
            Audio Recording (Optional)
          </label>
          
          {/* File input for audio */}
          {/* type="file" creates file picker */}
          {/* accept="audio/*" limits to audio files only */}
          {/* onChange is called when user selects a file */}
          <input
            type="file"
            id="audio"
            name="audio"
            accept="audio/*"
            onChange={handleAudioChange}
            className="form-control-file"
          />
          
          {/* Show selected file name and size */}
          {/* Only renders if audioFile is not null */}
          {audioFile && (
            <div className="file-selected">
              🎤 {audioFile.name} ({(audioFile.size / 1024).toFixed(1)} KB)
            </div>
          )}
          
          <small className="form-hint">
            Supported formats: WAV, MP3, M4A (maximum 10MB)
          </small>
        </div>
        
        {/* ========================================
            FORM FIELD: Image Upload (Optional)
            ======================================== */}
        
        <div className="form-group">
          <label htmlFor="image">
            Photo (Optional)
          </label>
          
          {/* File input for images */}
          {/* accept="image/*" limits to image files only */}
          <input
            type="file"
            id="image"
            name="image"
            accept="image/*"
            onChange={handleImageChange}
            className="form-control-file"
          />
          
          {/* Show selected file name and size */}
          {imageFile && (
            <div className="file-selected">
              📷 {imageFile.name} ({(imageFile.size / 1024).toFixed(1)} KB)
            </div>
          )}
          
          <small className="form-hint">
            Supported formats: JPG, PNG, HEIC (maximum 10MB)
          </small>
        </div>
        
        {/* ========================================
            SUBMIT BUTTON
            ======================================== */}
        
        <div className="form-actions">
          {/* Submit button */}
          {/* type="submit" triggers form onSubmit event */}
          {/* disabled={submitting} prevents clicking while submitting */}
          <button 
            type="submit" 
            className="btn-submit"
            disabled={submitting}
          >
            {/* Conditional text: shows different message while submitting */}
            {/* Ternary operator: condition ? ifTrue : ifFalse */}
            {submitting ? '⏳ Submitting...' : '🚀 Submit Incident Report'}
          </button>
          
          {/* Reset button */}
          {/* type="button" prevents form submission (default is submit) */}
          <button 
            type="button" 
            className="btn-reset"
            onClick={() => {
              // Reset all form fields to empty
              setFormData({ 
                source: '', 
                description: '', 
                location: '' 
              });
              
              // Clear file selections
              setAudioFile(null);
              setImageFile(null);
              
              // Clear any messages
              setSubmitError(null);
              setSubmitSuccess(false);
              
              // Clear file input elements
              // document.getElementById finds element by id
              const audioInput = document.getElementById('audio');
              const imageInput = document.getElementById('image');
              
              // Set value to empty string to clear file selection
              if (audioInput) audioInput.value = '';
              if (imageInput) imageInput.value = '';
              
              // Log for debugging
              console.log('Form reset');
            }}
            disabled={submitting}
          >
            🔄 Reset Form
          </button>
        </div>
        
      </form>
      
      {/* ========================================
          HELP TEXT
          ======================================== */}
      
      <div className="form-footer">
        <p>
          <strong>Note:</strong> Audio and image uploads will be processed by AI 
          to extract additional information. This happens automatically after submission.
        </p>
        <p style={{ marginTop: '10px', fontSize: '0.85rem' }}>
          Your submission will be reviewed by dispatchers and appropriate emergency 
          services will be notified based on incident severity and type.
        </p>
      </div>
      
    </div>
  )
}

export default SubmitIncidentForm