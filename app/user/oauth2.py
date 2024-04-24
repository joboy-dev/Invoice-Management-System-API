import os
from pathlib import Path
from dotenv import load_dotenv

from jose import JWTError, jwt
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    '''Function to create an access token'''
    
    # Create a copy of data to encode so as to not manipulate actual data
    data_to_encode = data.copy()
    
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data_to_encode.update({'exp': expire})
    
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

    # print(jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM))
