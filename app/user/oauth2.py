import os
from pathlib import Path
import uuid
from dotenv import load_dotenv
import datetime as dt

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.user import schemas

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 72

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_access_token(data: dict) -> str:
    '''Function to create an access token'''
    
    # Create a copy of data to encode so as to not manipulate actual data
    data_to_encode = data.copy()
    
    expire = dt.datetime.now(dt.UTC) + dt.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    data_to_encode.update({'exp': expire})
    
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(access_token: str) -> dict:
    '''Function to decode access token'''
    
    payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload


def verify_access_token(access_token: str, credentials_exception):
    '''Function to verify the access token in case it is expired or has an issue'''
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        id: uuid.UUID = payload.get('user_id')
        expire = dt.datetime.fromtimestamp(payload.get('exp'), tz=dt.UTC)
        
        if id is None:
            raise credentials_exception
        
        # if dt.datetime.now().replace(tzinfo=None) >= expire.replace(tzinfo=None):
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')
        
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception   
    
    return token_data.id
    

def get_current_user(access_token: str = Depends(oauth2_scheme)):
    '''Function to get the current logged in user based on the token provided'''
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Could not validate crenentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    
    return verify_access_token(access_token, credentials_exception)
