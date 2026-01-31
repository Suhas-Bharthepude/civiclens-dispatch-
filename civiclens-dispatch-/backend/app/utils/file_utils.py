# backend/app/utils/file_utils.py
# This file handles file upload operations
# It saves uploaded files to organized folders with unique names

# Import os module for file system operations
import os

# Import uuid for generating unique file names
import uuid

# Import UploadFile type from FastAPI
from fastapi import UploadFile

# Import config to get upload directory
from app.config import settings


def save_upload_file(file: UploadFile, subfolder: str) -> str:
    """
    Save an uploaded file to disk with a unique filename.
    
    Args:
        file: The uploaded file from FastAPI
        subfolder: Subfolder within media directory (e.g., "audio", "images")
    
    Returns:
        str: Relative path to the saved file
        
    Example:
        save_upload_file(audio_file, "audio")
        → Returns: "backend/app/media/tmp/audio/abc-123-def.wav"
    """
    
    # Build the full directory path
    # Example: backend/app/media/tmp/audio
    upload_path = os.path.join(settings.UPLOAD_DIR, subfolder)
    
    # Create directory if it doesn't exist
    # exist_ok=True prevents errors if directory already exists
    # parents=True creates parent directories if needed
    os.makedirs(upload_path, exist_ok=True)
    
    # Extract file extension from original filename
    # os.path.splitext splits "file.wav" into ("file", ".wav")
    _, file_extension = os.path.splitext(file.filename)
    
    # Generate unique filename using UUID
    # uuid4() creates a random unique identifier
    # This prevents filename collisions if multiple users upload same filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Build full path where file will be saved
    # Example: backend/app/media/tmp/audio/abc-123-def.wav
    file_path = os.path.join(upload_path, unique_filename)
    
    # Write file to disk in binary mode
    # "wb" = write binary (required for non-text files)
    with open(file_path, "wb") as buffer:
        # Read uploaded file contents and write to disk
        buffer.write(file.file.read())
    
    # Return the relative path (not absolute)
    # This is what we store in the database
    return file_path


def delete_file(file_path: str) -> bool:
    """
    Delete a file from disk.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        bool: True if file was deleted, False if file didn't exist
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        int: File size in bytes, or 0 if file doesn't exist
    """
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    except Exception as e:
        print(f"Error getting file size for {file_path}: {e}")
        return 0


def ensure_upload_dirs():
    """
    Ensure all required upload directories exist.
    Call this on application startup.
    """
    # List of subfolders we need
    subfolders = ["audio", "images", "documents"]
    
    for subfolder in subfolders:
        path = os.path.join(settings.UPLOAD_DIR, subfolder)
        os.makedirs(path, exist_ok=True)
        print(f"✅ Ensured directory exists: {path}")