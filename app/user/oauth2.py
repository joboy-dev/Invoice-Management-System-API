import os
from pathlib import Path
import uuid
from dotenv import load_dotenv
import datetime as dt

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.user import schemas, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def create_access_token(data: dict) -> str:
    '''Function to create an access token'''
    
    # Create a copy of data to encode so as to not manipulate actual data
    data_to_encode = data.copy()
    
    expire = dt.datetime.now(dt.UTC) + dt.timedelta(hours=settings.access_token_expire_hours)
    data_to_encode.update({'exp': expire})
    
    encoded_jwt = jwt.encode(data_to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(access_token: str) -> dict:
    '''Function to decode access token'''
    
    payload = jwt.decode(access_token, settings.secret_key, algorithms=[settings.algorithm])
    return payload


def verify_access_token(access_token: str, credentials_exception):
    '''Function to verify the access token in case it is expired or has an issue'''
    
    try:
        payload = jwt.decode(access_token, settings.secret_key, algorithms=[settings.algorithm])
        
        user_id: uuid.UUID = payload.get('user_id')
        
        if user_id is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(id=user_id)
    except JWTError:
        raise credentials_exception   
    
    return token_data
    

def get_current_user(access_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    '''Function to get the current logged in user based on the token provided'''
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail='Could not validate crenentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    
    token = verify_access_token(access_token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    
    return user
