// frontend/src/components/SubmitIncidentForm.jsx
// Form component for citizens to submit new incident reports
// Features: Controlled inputs, validation, file uploads, API integration
// Day 29: Enhanced with better error handling and troubleshooting

// Import React hooks
import { useState } from 'react'

// Import API function to create incidents
import { createIncident } from '../../api/client'

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
  const [formData, setFormData] = useState({
    source: '',         // Who is reporting (dropdown)
    description: '',    // What happened (textarea)
    location: ''        // Where it happened (text input)
  })
  
  // State: uploaded files (for future Day 31)
  const [audioFile, setAudioFile] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  
  // State: form submission status
  const [submitting, setSubmitting] = useState(false)  // Is form being submitted?
  const [submitSuccess, setSubmitSuccess] = useState(false)  // Was submission successful?
  const [submitError, setSubmitError] = useState(null)  // Error message if failed
  
  
  // ========================================
  // VALIDATION FUNCTION
  // ========================================
  
  // Validate form data before submission
  // Returns true if valid, false if invalid
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
  function handleInputChange(event) {
    const { name, value } = event.target;
    
    console.log(`Field "${name}" changed to:`, value);
    
    // Update formData state
    setFormData({
      ...formData,      // Copy all existing fields
      [name]: value     // Update the field that changed
    });
  }
  
  // Handle audio file selection
  function handleAudioChange(event) {
    const file = event.target.files[0];
    setAudioFile(file);
    
    if (file) {
      console.log('Audio file selected:', {
        name: file.name,
        size: file.size,
        type: file.type
      });
    }
  }
  
  // Handle image file selection
  function handleImageChange(event) {
    const file = event.target.files[0];
    setImageFile(file);
    
    if (file) {
      console.log('Image file selected:', {
        name: file.name,
        size: file.size,
        type: file.type
      });
    }
  }
  
  // Handle form submission
  async function handleSubmit(event) {
    // Prevent default form submission
    event.preventDefault();
    
    console.log('Form submitted with data:', formData);
    
    // Validate form data
    if (!validateForm()) {
      console.log('Validation failed');
      return;
    }
    
    // Set submitting state
    setSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);
    
    try {
      // Call API to create incident
      const newIncident = await createIncident(formData);
      
      console.log('Incident created successfully:', newIncident);
      
      // Show success message
      setSubmitSuccess(true);
      
      // Reset form fields
      setFormData({
        source: '',
        description: '',
        location: ''
      });
      
      // Clear file selections
      setAudioFile(null);
      setImageFile(null);
      
      // Reset file inputs
      const audioInput = document.getElementById('audio');
      const imageInput = document.getElementById('image');
      if (audioInput) audioInput.value = '';
      if (imageInput) imageInput.value = '';
      
      // Notify parent component
      if (onIncidentSubmitted) {
        onIncidentSubmitted();
      }
      
      // Hide success message after 5 seconds
      setTimeout(() => {
        setSubmitSuccess(false);
      }, 5000);
      
    } catch (error) {
      console.error('Failed to create incident:', error);
      setSubmitError(error.message);
      
    } finally {
      setSubmitting(false);
    }
  }
  
  
  // ========================================
  // RETURN JSX
  // ========================================
  
  return (
    <div className="submit-form-container">
      
      <h2>📝 Submit New Incident Report</h2>
      
      <p className="form-description">
        Report an emergency or incident. All fields marked with * are required.
      </p>
      
      {/* ========================================
          SUCCESS MESSAGE
          ======================================== */}
      
      {submitSuccess && (
        <div className="alert alert-success">
          <strong>✅ Success!</strong> Incident submitted successfully. 
          Dispatchers have been notified and will respond shortly.
        </div>
      )}
      
      {/* ========================================
          ERROR MESSAGE (Enhanced - Day 29)
          ======================================== */}
      
      {submitError && (
        <div className="alert alert-error">
          <strong>❌ Submission Failed</strong>
          <p style={{ margin: '8px 0' }}>{submitError}</p>
          
          {/* Troubleshooting tips - collapsible */}
          <details style={{ marginTop: '10px', fontSize: '0.9rem' }}>
            <summary style={{ cursor: 'pointer', fontWeight: '600' }}>
              💡 Troubleshooting tips
            </summary>
            <ul style={{ marginTop: '8px', paddingLeft: '20px', lineHeight: '1.6' }}>
              <li>Check that the backend server is running on port 8000</li>
              <li>Verify all required fields are filled correctly</li>
              <li>Ensure description is at least 10 characters</li>
              <li>Try refreshing the page</li>
              <li>Check your network connection</li>
            </ul>
          </details>
          
          {/* Clear error button */}
          <button
            type="button"
            onClick={() => {
              // Clear error message
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
      
      <form onSubmit={handleSubmit} className="incident-form">
        
        {/* ========================================
            SOURCE FIELD
            ======================================== */}
        
        <div className="form-group">
          <label htmlFor="source">
            Report Source: <span className="required">*</span>
          </label>
          
          <select
            id="source"
            name="source"
            value={formData.source}
            onChange={handleInputChange}
            required
            className="form-control"
          >
            <option value="">-- Select Source --</option>
            <option value="citizen">Citizen</option>
            <option value="police">Police</option>
            <option value="dispatcher">Dispatcher</option>
            <option value="sensor">Automated Sensor</option>
          </select>
        </div>
        
        {/* ========================================
            DESCRIPTION FIELD
            ======================================== */}
        
        <div className="form-group">
          <label htmlFor="description">
            Incident Description: <span className="required">*</span>
          </label>
          
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
          
          <small className="form-hint">
            {formData.description.length} characters
            {formData.description.length < 20 && ' (minimum 20 recommended)'}
          </small>
        </div>
        
        {/* ========================================
            LOCATION FIELD
            ======================================== */}
        
        <div className="form-group">
          <label htmlFor="location">
            Location: <span className="required">*</span>
          </label>
          
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
            AUDIO UPLOAD
            ======================================== */}
        
        <div className="form-group">
          <label htmlFor="audio">
            Audio Recording (Optional)
          </label>
          
          <input
            type="file"
            id="audio"
            name="audio"
            accept="audio/*"
            onChange={handleAudioChange}
            className="form-control-file"
          />
          
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
            IMAGE UPLOAD
            ======================================== */}
        
        <div className="form-group">
          <label htmlFor="image">
            Photo (Optional)
          </label>
          
          <input
            type="file"
            id="image"
            name="image"
            accept="image/*"
            onChange={handleImageChange}
            className="form-control-file"
          />
          
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
            FORM ACTIONS
            ======================================== */}
        
        <div className="form-actions">
          {/* Submit button */}
          <button 
            type="submit" 
            className="btn-submit"
            disabled={submitting}
          >
            {submitting ? '⏳ Submitting...' : '🚀 Submit Incident Report'}
          </button>
          
          {/* Reset button */}
          <button 
            type="button" 
            className="btn-reset"
            onClick={() => {
              // Reset all form fields
              setFormData({ 
                source: '', 
                description: '', 
                location: '' 
              });
              
              // Clear files
              setAudioFile(null);
              setImageFile(null);
              
              // Clear messages
              setSubmitError(null);
              setSubmitSuccess(false);
              
              // Clear file inputs
              const audioInput = document.getElementById('audio');
              const imageInput = document.getElementById('image');
              if (audioInput) audioInput.value = '';
              if (imageInput) imageInput.value = '';
              
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