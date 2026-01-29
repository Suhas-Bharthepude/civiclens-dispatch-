# Import the os module
# This lets us work with the operating system (paths, folders, files)
import os

# Import uuid
# uuid is used to generate unique file names so files don't overwrite each other
import uuid

# Import UploadFile from FastAPI
# UploadFile represents a file uploaded by the client
from fastapi import UploadFile


# Define a constant for the base upload directory
# All uploaded files will be stored inside this folder
UPLOAD_DIR = "uploads"


# Define a function that saves an uploaded file to disk
# It takes:
# - file: the uploaded file from FastAPI
# - subfolder: a folder inside UPLOAD_DIR (example: "audio")
def save_upload_file(file: UploadFile, subfolder: str) -> str:
    
    # Create the full directory path where the file will be stored
    # Example result: uploads/audio
    upload_path = os.path.join(UPLOAD_DIR, subfolder)

    # Create the directory if it does not already exist
    # exist_ok=True prevents errors if the folder already exists
    os.makedirs(upload_path, exist_ok=True)

    # Extract the original file extension (example: ".wav", ".mp3")
    # os.path.splitext splits filename into (name, extension)
    _, file_extension = os.path.splitext(file.filename)

    # Generate a unique filename using uuid
    # uuid4() creates a random unique ID
    # This prevents filename collisions
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Create the full file path where the file will be saved
    # Example: uploads/audio/abcd-1234.wav
    file_path = os.path.join(upload_path, unique_filename)

    # Open the destination file in binary write mode ("wb")
    # Binary mode is required for non-text files like audio
    with open(file_path, "wb") as buffer:
        
        # Read the uploaded file's contents and write them to disk
        buffer.write(file.file.read())

    # Return the file path so it can be saved in the database
    return file_path
