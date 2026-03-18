// frontend/src/components/shared/AudioUploader.jsx
// Component for uploading audio files with progress tracking
// Features: File validation, upload progress, error handling

// Import React hooks
import { useState } from 'react'

// Import upload function from API client
import { uploadAudio } from '../../api/client'

// Import CSS
import './AudioUploader.css'


// ========================================
// AUDIO UPLOADER COMPONENT
// ========================================

// Component for uploading audio files to backend
// Props:
//   - incidentId: ID of incident to attach audio to
//   - onUploadComplete: Callback when upload finishes successfully
//   - onUploadError: Callback when upload fails
function AudioUploader({ incidentId, onUploadComplete, onUploadError }) {
  
  // ========================================
  // STATE
  // ========================================
  
  // State: selected audio file (null if no file selected)
  const [audioFile, setAudioFile] = useState(null)
  
  // State: upload in progress
  const [uploading, setUploading] = useState(false)
  
  // State: upload progress (0-100 percentage)
  const [uploadProgress, setUploadProgress] = useState(0)
  
  // State: upload error message
  const [uploadError, setUploadError] = useState(null)
  
  
  // ========================================
  // FILE VALIDATION
  // ========================================
  
  // Validate audio file before upload
  // Returns true if valid, false if invalid (with error message)
  function validateAudioFile(file) {
    // Check file exists
    if (!file) {
      setUploadError('No file selected');
      return false;
    }
    
    // Check file size (max 10MB)
    // file.size is in bytes
    // 10MB = 10 * 1024 * 1024 bytes = 10,485,760 bytes
    const maxSize = 10 * 1024 * 1024;  // 10MB in bytes
    
    if (file.size > maxSize) {
      // File too large
      const sizeMB = (file.size / 1024 / 1024).toFixed(2);
      setUploadError(`File too large (${sizeMB}MB). Maximum size is 10MB.`);
      return false;
    }
    
    // Check file type
    // file.type is MIME type (e.g., "audio/mp3", "audio/wav")
    const allowedTypes = ['audio/mp3', 'audio/mpeg', 'audio/wav', 'audio/m4a', 'audio/x-m4a', 'audio/ogg'];
    
    if (!allowedTypes.includes(file.type)) {
      setUploadError(`Invalid file type: ${file.type}. Please upload WAV, MP3, or M4A.`);
      return false;
    }
    
    // All validations passed
    return true;
  }
  
  
  // ========================================
  // EVENT HANDLERS
  // ========================================
  
  // Handle file selection from input
  function handleFileSelect(event) {
    // Get selected file from input
    // event.target.files is FileList (array-like)
    // [0] gets first file
    const file = event.target.files[0];
    
    // Clear any previous error
    setUploadError(null);
    
    // If file selected
    if (file) {
      // Validate file
      if (validateAudioFile(file)) {
        // Store in state if valid
        setAudioFile(file);
        
        // Log for debugging
        console.log('Audio file selected:', {
          name: file.name,
          size: `${(file.size / 1024).toFixed(1)} KB`,
          type: file.type
        });
      } else {
        // Validation failed (error already set by validateAudioFile)
        // Clear file input
        event.target.value = '';
      }
    }
  }
  
  // Handle upload button click
  async function handleUpload() {
    // Validate file again before upload (in case state is stale)
    if (!validateAudioFile(audioFile)) {
      return;
    }
    
    // Clear any previous error
    setUploadError(null);
    
    // Set uploading state
    setUploading(true);
    
    // Reset progress
    setUploadProgress(0);
    
    try {
      // Log upload start
      console.log(`Uploading audio to incident ${incidentId}...`);
      
      // Simulate progress (in real implementation, track actual progress)
      // For now, we'll use setTimeout to simulate progress
      // Real progress tracking requires XMLHttpRequest instead of fetch
      
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          // Increment progress
          const newProgress = prev + 10;
          
          // Stop at 90% (wait for actual upload to complete)
          return newProgress >= 90 ? 90 : newProgress;
        });
      }, 200);  // Update every 200ms
      
      // Call API to upload file
      // This sends file to backend via FormData
      const result = await uploadAudio(incidentId, audioFile);
      
      // Clear progress interval
      clearInterval(progressInterval);
      
      // Set progress to 100% (complete)
      setUploadProgress(100);
      
      // Log success
      console.log('Audio upload complete:', result);
      
      // Call success callback if provided
      if (onUploadComplete) {
        onUploadComplete(result);
      }
      
      // Reset after short delay (let user see 100%)
      setTimeout(() => {
        setAudioFile(null);
        setUploadProgress(0);
        setUploading(false);
        
        // Clear file input
        const input = document.getElementById('audio-upload-input');
        if (input) input.value = '';
      }, 1500);
      
    } catch (error) {
      // Upload failed
      console.error('Audio upload failed:', error);
      
      // Set error state
      setUploadError(error.message);
      
      // Call error callback if provided
      if (onUploadError) {
        onUploadError(error);
      }
      
      // Reset uploading state
      setUploading(false);
      setUploadProgress(0);
    }
  }
  
  // Handle cancel/remove file
  function handleRemove() {
    // Clear selected file
    setAudioFile(null);
    
    // Clear error
    setUploadError(null);
    
    // Reset progress
    setUploadProgress(0);
    
    // Clear file input element
    const input = document.getElementById('audio-upload-input');
    if (input) input.value = '';
    
    console.log('Audio file removed');
  }
  
  
  // ========================================
  // RENDER
  // ========================================
  
  return (
    <div className="audio-uploader">
      
      {/* ========================================
          FILE INPUT
          ======================================== */}
      
      {!audioFile && !uploading && (
        // Show file input if no file selected and not uploading
        <div className="audio-input-container">
          <label htmlFor="audio-upload-input" className="audio-label">
            🎤 Select Audio File
          </label>
          
          <input
            id="audio-upload-input"
            type="file"
            accept="audio/*"
            onChange={handleFileSelect}
            className="audio-input"
          />
          
          <p className="audio-hint">
            Supported: WAV, MP3, M4A (max 10MB)
          </p>
        </div>
      )}
      
      {/* ========================================
          SELECTED FILE PREVIEW
          ======================================== */}
      
      {audioFile && !uploading && (
        // Show file info and upload button
        <div className="audio-selected">
          <div className="audio-file-info">
            <span className="audio-icon">🎤</span>
            <div className="audio-details">
              <p className="audio-filename">{audioFile.name}</p>
              <p className="audio-filesize">
                {(audioFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>
          
          <div className="audio-actions">
            <button
              onClick={handleUpload}
              className="btn-upload"
            >
              ⬆️ Upload
            </button>
            
            <button
              onClick={handleRemove}
              className="btn-remove"
            >
              🗑️ Remove
            </button>
          </div>
        </div>
      )}
      
      {/* ========================================
          UPLOAD PROGRESS
          ======================================== */}
      
      {uploading && (
        // Show progress bar while uploading
        <div className="audio-uploading">
          <p className="upload-status">⏳ Uploading audio...</p>
          
          {/* HTML5 progress element */}
          <progress 
            value={uploadProgress} 
            max={100}
            className="upload-progress-bar"
          />
          
          <p className="upload-percentage">
            {Math.round(uploadProgress)}%
          </p>
        </div>
      )}
      
      {/* ========================================
          ERROR MESSAGE
          ======================================== */}
      
      {uploadError && (
        // Show error if upload or validation failed
        <div className="upload-error">
          <p>❌ {uploadError}</p>
          
          <button
            onClick={() => setUploadError(null)}
            className="btn-clear-error"
          >
            Clear
          </button>
        </div>
      )}
      
    </div>
  )
}

export default AudioUploader