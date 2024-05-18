import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi import HTTPException, status, UploadFile

BASE_DIR = Path(__file__).resolve().parent.parent

def get_value_from_env(key):
    '''Function to get a value from .env file'''
    
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    return os.getenv(key)


async def upload_file(file, allowed_extensions: list | None, upload_folder: str, new_filename: str):
    '''Function to upload a file'''
    
    # Check against invalid extensions
    file_name = file.filename.lower()
    file_extension = file_name.split('.')[-1]
    
    if allowed_extensions:
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file format')
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        os.system(f'mkdir uploads')
    
    # Create file storage path
    UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads', upload_folder)
    if not os.path.exists(UPLOAD_DIR):
        os.system(f'mkdir uploads\{upload_folder}')
    
    # Generate a new file name
    SAVE_FILE_DIR = os.path.join(UPLOAD_DIR, new_filename)
    
    with open(SAVE_FILE_DIR, 'wb') as f:
        content = await file.read()
        f.write(content)
        
    return {
        'filename': new_filename,
        'filepath': SAVE_FILE_DIR
    } 
    