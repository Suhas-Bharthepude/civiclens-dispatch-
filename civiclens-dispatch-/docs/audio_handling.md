# Audio Handling Guide (Day 31)

## Supported Audio Formats

### WAV (Waveform Audio File)
- **Extension:** `.wav`
- **MIME Type:** `audio/wav`, `audio/x-wav`
- **Compression:** Uncompressed
- **Quality:** Lossless (highest quality)
- **File Size:** Large (1 min ≈ 10MB)
- **Best for:** AI processing (no quality loss)

### MP3 (MPEG Audio Layer 3)
- **Extension:** `.mp3`
- **MIME Type:** `audio/mp3`, `audio/mpeg`
- **Compression:** Lossy
- **Quality:** Good (adjustable bitrate)
- **File Size:** Small (1 min ≈ 1MB at 128kbps)
- **Best for:** General use, storage efficiency

### M4A (MPEG-4 Audio)
- **Extension:** `.m4a`
- **MIME Type:** `audio/m4a`, `audio/x-m4a`
- **Compression:** Lossy (AAC codec)
- **Quality:** Excellent
- **File Size:** Small (1 min ≈ 0.8MB)
- **Best for:** iPhone recordings

### OGG/WebM
- **Extension:** `.ogg`, `.webm`
- **MIME Type:** `audio/ogg`, `audio/webm`
- **Compression:** Lossy
- **Quality:** Good
- **File Size:** Small
- **Best for:** Browser recordings

## File Size Limits

### Current Limit: 10MB

**Why 10MB:**
- Covers most phone recordings (up to 10 minutes)
- Prevents server overload
- Reasonable upload time on slow connections

**File size examples:**
- 1 min WAV @ 16kHz: ~2MB
- 1 min MP3 @ 128kbps: ~1MB
- 5 min MP3: ~5MB
- 10 min MP3: ~10MB (at limit)

### Enforced Where

**Frontend (client.js):**
- Validates before upload
- Shows error if too large
- Better UX (fails fast)

**Backend (FastAPI):**
- Also validates (safety)
- Rejects oversized files
- Returns 413 Payload Too Large

## Upload Workflow

### Step-by-Step Process
```
1. User selects audio file
   ↓
2. Frontend validates (size, type)
   ↓
3. User submits form
   ↓
4. Create incident (POST /incidents)
   ↓ Returns: {id: 11, ...}
   ↓
5. Upload audio (POST /incidents/11/audio)
   ↓ FormData with file
   ↓
6. Backend saves to disk
   ↓ Stores path in database
   ↓
7. Background job processes audio
   ↓ Transcribes with ASR model (Day 33-34)
   ↓
8. Transcript stored in database
   ↓
9. Dispatcher sees transcript in UI
```

### Technical Flow

**Frontend:**
```javascript
// 1. Create incident
const incident = await createIncident(formData);

// 2. Upload audio to that incident
if (audioFile) {
    await uploadAudio(incident.id, audioFile);
}

// 3. Backend processes asynchronously
// 4. Transcript appears when processed
```

**Backend:**
```python
@app.post("/incidents/{id}/audio")
async def upload_audio(id: int, file: UploadFile):
    # Save file
    path = save_upload_file(file, "audio")
    
    # Update incident
    await db.execute(
        incidents.update()
        .where(id == id)
        .values(audio_path=path)
    )
    
    # Trigger background processing
    background_tasks.add_task(process_incident, id)
    
    return {"message": "Success", "audio_path": path}
```

## File Validation

### Frontend Validation
```javascript
function validateAudio(file) {
    // Check exists
    if (!file) return false;
    
    // Check size
    if (file.size > 10 * 1024 * 1024) {
        throw new Error("File too large");
    }
    
    // Check type
    const allowed = ['audio/mp3', 'audio/wav', 'audio/m4a'];
    if (!allowed.includes(file.type)) {
        throw new Error("Invalid file type");
    }
    
    return true;
}
```

### Backend Validation
```python
# In backend (already implemented)
def save_upload_file(file: UploadFile):
    # Check file extension
    # Check file size
    # Validate MIME type
    # Save with unique UUID filename
```

## Upload Progress

### Current Implementation

**Simulated progress:**
- Progress updates every 200ms
- Goes from 0% → 90% during upload
- Jumps to 100% when complete

**Why simulated:**
- `fetch()` API doesn't support progress events
- Would need XMLHttpRequest for real progress
- Good enough for files < 10MB (upload fast)

### Future: Real Progress
```javascript
// Would require XMLHttpRequest
const xhr = new XMLHttpRequest();

xhr.upload.onprogress = (event) => {
    const percent = (event.loaded / event.total) * 100;
    setUploadProgress(percent);
};

xhr.open('POST', url);
xhr.send(formData);
```

## Storage

### Current: Local Disk

**Location:** `backend/app/media/tmp/audio/`

**Filename:** UUID + original extension
- Example: `a1b2c3d4-e5f6-7890-abcd-ef1234567890.mp3`

**Database:** Stores path as string
- Example: `"backend/app/media/tmp/audio/a1b2c3d4...mp3"`

### Future: S3/Cloud Storage (Day 50+)

**Benefits:**
- Unlimited storage
- CDN integration (fast access)
- Automatic backups
- Scalability

**Implementation:**
- boto3 (AWS SDK)
- Upload to S3 bucket
- Store S3 URL in database

## Error Handling

### Common Errors

**"File too large"**
- Cause: File > 10MB
- Solution: Compress audio or split into parts
- Frontend catches before upload

**"Invalid file type"**
- Cause: Not an audio file
- Solution: Select WAV, MP3, or M4A
- Frontend shows allowed types

**"Upload failed"**
- Cause: Network error, server down
- Solution: Retry button
- Backend might be offline

**"Incident not found"**
- Cause: Trying to upload to non-existent incident
- Solution: Create incident first
- Should never happen in normal flow

## Best Practices

✅ Validate on frontend (better UX)  
✅ Validate on backend (security)  
✅ Show upload progress  
✅ Allow retry on failure  
✅ Support common formats  
✅ Clear error messages  
✅ Log all steps  

❌ Don't trust frontend validation alone  
❌ Don't upload before creating incident  
❌ Don't ignore file size limits  
❌ Don't upload synchronously (use async)  

## Testing Audio Uploads

### Manual Test

1. Create small MP3 file (< 1MB)
2. Fill incident form
3. Attach audio
4. Submit
5. Check backend logs
6. Verify file in `backend/app/media/tmp/audio/`
7. Check database for audio_path

### Test Cases

- ✅ Valid MP3 upload
- ✅ Valid WAV upload
- ✅ File too large (> 10MB)
- ✅ Invalid file type (PDF, TXT)
- ✅ No file selected
- ✅ Network error during upload
- ✅ Backend offline

---

*Audio handling documented: Day 31*