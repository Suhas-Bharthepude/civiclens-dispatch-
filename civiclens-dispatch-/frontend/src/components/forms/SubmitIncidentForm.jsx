// frontend/src/components/forms/SubmitIncidentForm.jsx
// Form component for citizens to submit new incident reports
// Features: Controlled inputs, validation, file uploads, API integration
// Day 29: Enhanced with better error handling and troubleshooting
// Day 31: Implements actual audio/image file uploads to backend

// Import React hooks
import { useState } from 'react'

// Import API functions for creating incidents and uploading files
import { createIncident, uploadAudio, uploadImage } from '../../api/client'

// Import CSS
import './SubmitIncidentForm.css'


// ========================================
// SUBMIT INCIDENT FORM COMPONENT
// ========================================

// Component that renders incident submission form
// Props:
//   - onIncidentSubmitted: Callback function to notify parent when incident is created
function SubmitIncidentForm({ onSubmitted }) {
  
  // ========================================
  // STATE - Form Data
  // ========================================
  
  // State: form field values
  // All inputs are controlled by React state
  // This object contains all text field values
  const [formData, setFormData] = useState({
    source: '',         // Who is reporting (dropdown selection)
    description: '',    // What happened (textarea text)
    location: ''        // Where it happened (text input)
  })
  
  // State: uploaded files
  // Store File objects when user selects files
  const [audioFile, setAudioFile] = useState(null)  // Audio File object or null
  const [imageFile, setImageFile] = useState(null)  // Image File object or null
  
  // State: form submission status
  // These control what messages to show and whether buttons are disabled
  const [submitting, setSubmitting] = useState(false)       // Is form currently being submitted?
  const [submitSuccess, setSubmitSuccess] = useState(false) // Did submission succeed?
  const [submitError, setSubmitError] = useState(null)      // Error message if submission failed
  
  
  // ========================================
  // VALIDATION FUNCTION
  // ========================================
  
  // Validate form data before submission
  // Checks all required fields and constraints
  // Returns true if valid, false if invalid
  // Sets error message in state if validation fails
  function validateForm() {
    // Clear any existing error message first
    // This removes old errors when user tries again
    setSubmitError(null);
    
    // Check if source dropdown has a value selected
    // Empty string means placeholder "-- Select Source --" is still selected
    if (formData.source === '') {
      setSubmitError('Please select a report source');
      return false;
    }
    
    // Check description meets minimum length requirement
    // .length counts number of characters in string
    // Minimum 10 characters ensures meaningful description
    if (formData.description.length < 10) {
      setSubmitError('Description must be at least 10 characters');
      return false;
    }
    
    // Check location is not empty
    // .trim() removes whitespace from start and end
    // This catches cases where user just typed spaces
    if (formData.location.trim() === '') {
      setSubmitError('Location is required');
      return false;
    }
    
    // All validations passed!
    // Form data is valid and ready to submit
    return true;
  }
  
  
  // ========================================
  // EVENT HANDLERS
  // ========================================
  
  // Handle changes to text inputs, textareas, and select dropdowns
  // This function is called every time user types or selects
  function handleInputChange(event) {
    // Extract name and value from the input that changed
    // event.target is the input element
    // name = the 'name' attribute (e.g., "description")
    // value = the current value of the input
    const { name, value } = event.target;
    
    // Log for debugging - see what's being typed
    console.log(`Field "${name}" changed to:`, value);
    
    // Update formData state
    // Use spread operator (...) to copy all existing fields
    // Then override the specific field that changed
    // [name] uses the variable value as the object key (dynamic key)
    setFormData({
      ...formData,      // Copy source, description, location
      [name]: value     // Update only the field that changed
    });
    
    // Example: User types "F" in description
    // Before: { source: 'citizen', description: '', location: '123 St' }
    // name = "description", value = "F"
    // After: { source: 'citizen', description: 'F', location: '123 St' }
  }
  
  // Handle audio file selection from file input
  // Called when user clicks "Choose File" and selects an audio file
  function handleAudioChange(event) {
    // Get the selected file from the input
    // event.target.files is a FileList (array-like object)
    // [0] gets the first file (file inputs are single-file by default)
    const file = event.target.files[0];
    
    // Store the File object in state
    // This lets us access it later for upload
    setAudioFile(file);
    
    // Log file details for debugging
    // Only log if file was actually selected (user didn't click cancel)
    if (file) {
      console.log('Audio file selected:', {
        name: file.name,      // Filename: "recording.mp3"
        size: file.size,      // Size in bytes: 1048576
        type: file.type       // MIME type: "audio/mp3"
      });
    }
  }
  
  // Handle image file selection from file input
  // Same pattern as audio file handling
  function handleImageChange(event) {
    // Get the selected file
    const file = event.target.files[0];
    
    // Store in state
    setImageFile(file);
    
    // Log details
    if (file) {
      console.log('Image file selected:', {
        name: file.name,      // Filename: "photo.jpg"
        size: file.size,      // Size in bytes
        type: file.type       // MIME type: "image/jpeg"
      });
    }
  }
  
  // Handle form submission
  // This is the main function - creates incident and uploads files
  async function handleSubmit(event) {
    // CRITICAL: Prevent default form submission behavior
    // Without this, page would reload (old HTML form behavior)
    // We want to handle submission with JavaScript instead
    event.preventDefault();
    
    // Log that form is being submitted
    console.log('Form submitted with data:', formData);
    console.log('Audio file:', audioFile ? audioFile.name : 'none');
    console.log('Image file:', imageFile ? imageFile.name : 'none');
    
    // Validate form data before submitting to API
    // If validation fails, stop here and show error
    if (!validateForm()) {
      console.log('Validation failed - stopping submission');
      return;  // Exit function early
    }
    
    // Set submitting state to true
    // This disables submit button (prevents double-submission)
    // Also changes button text to "Submitting..."
    setSubmitting(true);
    
    // Clear any previous messages
    setSubmitError(null);
    setSubmitSuccess(false);
    
    try {
      // ========================================
      // STEP 1: Create the incident in database
      // ========================================
      
      console.log('Step 1: Creating incident...');
      
      // Call API to create incident
      // Makes POST request to http://localhost:8000/incidents
      // Sends formData (source, description, location) as JSON
      // Backend validates, saves to database, returns created incident
      const newIncident = await createIncident(formData);
      
      // Log the created incident object
      console.log('✅ Incident created successfully:', newIncident);
      
      // Extract the incident ID from response
      // We need this ID to upload files to the correct incident
      // Backend auto-generates this ID when incident is created
      const incidentId = newIncident.id;
      console.log('New incident ID:', incidentId);
      
      
      // ========================================
      // STEP 2: Upload audio file if user selected one
      // ========================================
      
      // Only attempt upload if audioFile is not null
      // User might not have selected an audio file (it's optional)
      if (audioFile) {
        try {
          console.log('Step 2: Uploading audio file to incident', incidentId);
          
          // Upload audio file to backend
          // Makes POST request to /incidents/{incidentId}/audio
          // Sends file as multipart/form-data
          // Backend saves file to disk and updates incident.audio_path in database
          const audioResult = await uploadAudio(incidentId, audioFile);
          
          // Log success
          console.log('✅ Audio uploaded successfully:', audioResult);
          console.log('   Audio saved to:', audioResult.audio_path);
          
        } catch (audioError) {
          // If audio upload fails, log error but DON'T fail entire submission
          // The incident was still created successfully (step 1 succeeded)
          // Audio is supplementary - not critical to incident creation
          console.error('⚠️ Audio upload failed (incident still created):', audioError);
          
          // Note: We could show a warning toast here (future enhancement)
          // For now, we just log it - user sees incident was created
        }
      } else {
        console.log('Step 2: No audio file to upload (skipping)');
      }
      
      
      // ========================================
      // STEP 3: Upload image file if user selected one
      // ========================================
      
      // Only attempt upload if imageFile is not null
      if (imageFile) {
        try {
          console.log('Step 3: Uploading image file to incident', incidentId);
          
          // Upload image file to backend
          // Makes POST request to /incidents/{incidentId}/image
          // Sends file as multipart/form-data
          // Backend saves file to disk and updates incident.image_path
          const imageResult = await uploadImage(incidentId, imageFile);
          
          // Log success
          console.log('✅ Image uploaded successfully:', imageResult);
          console.log('   Image saved to:', imageResult.image_path);
          
        } catch (imageError) {
          // If image upload fails, log error but don't fail entire submission
          // Same reasoning as audio - incident creation succeeded
          console.error('⚠️ Image upload failed (incident still created):', imageError);
        }
      } else {
        console.log('Step 3: No image file to upload (skipping)');
      }
      
      
      // ========================================
      // STEP 4: Show success and reset form
      // ========================================
      
      console.log('✅ All steps complete! Incident submitted successfully.');
      
      // Show green success message to user
      setSubmitSuccess(true);
      
      // Reset form fields to empty
      // Clears the form for next submission
      setFormData({
        source: '',
        description: '',
        location: ''
      });
      
      // Clear file selections from state
      setAudioFile(null);
      setImageFile(null);
      
      // Reset file input elements (clear the selected file names shown in UI)
      // getElementById finds the <input> element by its id attribute
      const audioInput = document.getElementById('audio');
      const imageInput = document.getElementById('image');
      
      // Set value to empty string to clear file selection
      if (audioInput) audioInput.value = '';
      if (imageInput) imageInput.value = '';
      
      // Notify parent component that incident was submitted
      // Parent (App.jsx) will increment refreshTrigger
      // This causes IncidentsList to re-fetch and show the new incident
      if (onSubmitted) {
        onSubmitted();
      }
      
      // Hide success message after 5 seconds
      // setTimeout runs a function after a delay (milliseconds)
      setTimeout(() => {
        setSubmitSuccess(false);
      }, 5000);  // 5000ms = 5 seconds
      
    } catch (error) {
      // If incident creation (step 1) fails, catch the error
      // This is the only error that stops the entire process
      // File upload errors are caught separately and don't trigger this
      console.error('❌ Failed to create incident:', error);
      
      // Show error message to user
      setSubmitError(error.message);
      
    } finally {
      // Always turn off submitting state (whether success or error)
      // finally block runs regardless of try/catch outcome
      // This re-enables the submit button
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
      
      {/* Form description/instructions */}
      <p className="form-description">
        Report an emergency or incident. All fields marked with * are required.
      </p>
      
      {/* ========================================
          SUCCESS MESSAGE
          ======================================== */}
      
      {/* Only render success message if submitSuccess is true */}
      {/* && means: if left is truthy, render right side */}
      {submitSuccess && (
        <div className="alert alert-success">
          <strong>✅ Success!</strong> Incident submitted successfully. 
          Dispatchers have been notified and will respond shortly.
        </div>
      )}
      
      {/* ========================================
          ERROR MESSAGE (Enhanced - Day 29)
          ======================================== */}
      
      {/* Only render error message if submitError is not null */}
      {submitError && (
        <div className="alert alert-error">
          {/* Error heading */}
          <strong>❌ Submission Failed</strong>
          
          {/* Display the actual error message */}
          {/* {submitError} embeds the error text from state */}
          <p style={{ margin: '8px 0' }}>{submitError}</p>
          
          {/* Troubleshooting tips - collapsible details element */}
          {/* <details> creates expandable/collapsible section */}
          {/* <summary> is the clickable header */}
          <details style={{ marginTop: '10px', fontSize: '0.9rem' }}>
            <summary style={{ cursor: 'pointer', fontWeight: '600' }}>
              💡 Troubleshooting tips
            </summary>
            
            {/* List of helpful suggestions */}
            {/* Helps user diagnose and fix the problem */}
            <ul style={{ marginTop: '8px', paddingLeft: '20px', lineHeight: '1.6' }}>
              <li>Check that the backend server is running on port 8000</li>
              <li>Verify all required fields are filled correctly</li>
              <li>Ensure description is at least 10 characters</li>
              <li>Try refreshing the page</li>
              <li>Check your network connection</li>
            </ul>
          </details>
          
          {/* Clear error button */}
          {/* Allows user to dismiss error message */}
          <button
            type="button"
            onClick={() => {
              // Clear error message from state
              // Error box will disappear
              setSubmitError(null);
            }}
            style={{
              marginTop: '10px',
              padding: '8px 16px',
              backgroundColor: '#c0392b',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Clear Error
          </button>
        </div>
      )}
      
      {/* ========================================
          FORM ELEMENT
          ======================================== */}
      
      {/* The <form> element wraps all input fields */}
      {/* onSubmit is called when form is submitted */}
      {/* (user clicks submit button or presses Enter in text field) */}
      <form onSubmit={handleSubmit} className="incident-form">
        
        {/* ========================================
            FORM FIELD: Source (Dropdown)
            ======================================== */}
        
        <div className="form-group">
          {/* Label for accessibility */}
          {/* htmlFor links to input with matching id */}
          <label htmlFor="source">
            Report Source: <span className="required">*</span>
          </label>
          
          {/* Select dropdown input */}
          <select
            id="source"                      // ID for label linking
            name="source"                    // Name used in handleInputChange
            value={formData.source}          // Controlled by React state
            onChange={handleInputChange}     // Update state on change
            required                         // HTML5 validation (can't be empty)
            className="form-control"         // CSS class for styling
          >
            {/* Placeholder option with empty value */}
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
          
          {/* Textarea for multi-line text input */}
          <textarea
            id="description"                 // ID for label
            name="description"               // Name for handleInputChange
            value={formData.description}     // Controlled value
            onChange={handleInputChange}     // Update on change
            rows="5"                         // Initial height (5 rows)
            placeholder="Describe what happened in detail..."  // Hint text
            required                         // Must be filled
            className="form-control"         // CSS styling
          />
          
          {/* Character count helper text */}
          {/* Shows current length and warning if too short */}
          <small className="form-hint">
            {formData.description.length} characters
            {/* Conditional: only show warning if less than 20 */}
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
          
          {/* Single-line text input for location */}
          <input
            type="text"                      // Text input type
            id="location"                    // ID for label
            name="location"                  // Name for handleInputChange
            value={formData.location}        // Controlled value
            onChange={handleInputChange}     // Update on change
            placeholder="123 Main Street, City, State"  // Example text
            required                         // Must be filled
            className="form-control"         // CSS styling
          />
          
          {/* Helper text with tips */}
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
          
          {/* File input for audio files */}
          <input
            type="file"                      // File input type
            id="audio"                       // ID for label
            name="audio"                     // Name attribute
            accept="audio/*"                 // Only allow audio files (browser filter)
            onChange={handleAudioChange}     // Handle file selection
            className="form-control-file"    // CSS styling
          />
          
          {/* Show selected file info if file is selected */}
          {/* Only renders if audioFile is not null */}
          {audioFile && (
            <div className="file-selected">
              {/* Show file name and size */}
              {/* (file.size / 1024) converts bytes to KB */}
              {/* .toFixed(1) rounds to 1 decimal place */}
              🎤 {audioFile.name} ({(audioFile.size / 1024).toFixed(1)} KB)
            </div>
          )}
          
          {/* Helper text showing allowed formats */}
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
          
          {/* File input for image files */}
          <input
            type="file"                      // File input type
            id="image"                       // ID for label
            name="image"                     // Name attribute
            accept="image/*"                 // Only allow image files
            onChange={handleImageChange}     // Handle file selection
            className="form-control-file"    // CSS styling
          />
          
          {/* Show selected file info */}
          {imageFile && (
            <div className="file-selected">
              📷 {imageFile.name} ({(imageFile.size / 1024).toFixed(1)} KB)
            </div>
          )}
          
          {/* Helper text */}
          <small className="form-hint">
            Supported formats: JPG, PNG, HEIC (maximum 10MB)
          </small>
        </div>
        
        {/* ========================================
            FORM ACTIONS (Buttons)
            ======================================== */}
        
        <div className="form-actions">
          {/* Submit button */}
          {/* type="submit" triggers form onSubmit event */}
          {/* disabled when submitting prevents double-submission */}
          <button 
            type="submit" 
            className="btn-submit"
            disabled={submitting}
          >
            {/* Conditional button text */}
            {/* Shows different text while submitting */}
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
              const audioInput = document.getElementById('audio');
              const imageInput = document.getElementById('image');
              if (audioInput) audioInput.value = '';
              if (imageInput) imageInput.value = '';
              
              // Log for debugging
              console.log('Form reset to empty state');
            }}
            disabled={submitting}
          >
            🔄 Reset Form
          </button>
        </div>
        
      </form>
      
      {/* ========================================
          HELP TEXT / FOOTER
          ======================================== */}
      
      <div className="form-footer">
        {/* Note about AI processing */}
        <p>
          <strong>Note:</strong> Audio and image uploads will be processed by AI 
          to extract additional information. This happens automatically after submission.
        </p>
        
        {/* Additional context */}
        <p style={{ marginTop: '10px', fontSize: '0.85rem' }}>
          Your submission will be reviewed by dispatchers and appropriate emergency 
          services will be notified based on incident severity and type.
        </p>
      </div>
      
    </div>
  )
}

// ========================================
// EXPORT
// ========================================

// Export component as default
// Allows importing: import SubmitIncidentForm from './SubmitIncidentForm'
export default SubmitIncidentForm