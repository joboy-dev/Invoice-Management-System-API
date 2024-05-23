import os
from pathlib import Path
from secrets import token_hex
import uuid
from dotenv import load_dotenv

from fastapi import HTTPException, status
from firebase_admin import storage, credentials, initialize_app
import pyrebase

from .firebase_config import firebase_config

BASE_DIR = Path(__file__).resolve().parent.parent

def get_value_from_env(key):
    '''Function to get a value from .env file'''
    
    load_dotenv(os.path.join(BASE_DIR, ".env"))
    return os.getenv(key)


async def upload_file(file, allowed_extensions: list | None, upload_folder: str, model_id: uuid.UUID):
    '''Function to upload a file'''
    
    # Check against invalid extensions
    file_name = file.filename.lower()
    
    file_extension = file_name.split('.')[-1]
    name = file_name.split('.')[0]
    
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File cannot be blank')
    
    if allowed_extensions:
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file format')
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        os.system(f'mkdir uploads')
    
    # Create file storage path
    UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads', upload_folder, f'{model_id}')
    if not os.path.exists(UPLOAD_DIR):
        os.system(f'mkdir uploads\{upload_folder}\{model_id}')
    
    # Generate a new file name
    new_filename = f'{name}-{token_hex(5)}.jpg'
    SAVE_FILE_DIR = os.path.join(UPLOAD_DIR, new_filename)
    
    with open(SAVE_FILE_DIR, 'wb') as f:
        content = await file.read()
        f.write(content)
    
    # Initailize firebase
    firebase = pyrebase.initialize_app(firebase_config)
    
    # Set up storage and a storage path for each file
    storage = firebase.storage()
    firebase_storage_path = f'invoice_api/{upload_folder}/{model_id}/{new_filename}'
    
    # Store the file in the firebase storage path
    storage.child(firebase_storage_path).put(SAVE_FILE_DIR)
    
    # Get download URL
    download_url = storage.child(firebase_storage_path).get_url(None)
    
    return {
        'file_name': new_filename,
        'download_url': download_url
    } 
    