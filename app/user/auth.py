from datetime import datetime
import os
from pathlib import Path
import uuid
from dotenv import load_dotenv
from fastapi import APIRouter, Request, status, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.user import oauth2, permissions
from app.user.utils import Utils

from . import models
from . import schemas

from app.database import get_db
from app.config import settings

auth_router = APIRouter(tags=['Authentication'])

def send_verification_mail(user: models.User):
    '''Function to send verification email to a user.'''
    
    if settings.debug:
        base_url = 'http://127.0.0.1:8000'
    else:
        base_url = 'production url'
        
    token = oauth2.create_access_token({'user_id': f'{user.id}'})
    url = f'{base_url}/email/verify?token={token}'
    
    Utils.send_email({
        'subject': 'Verify your email address',
        'body': f'Hello {user.first_name},\n\nThanks for signing up on our invoice management system. You need to verify your email address.\nClick the link below to do that:\n{url}.\nIf you did not request for this link, kindly ignore it.\n\nThank you.',
        'email': user.email
    })

# ----------------------------------------------------------------------------------------------------  
# ----------------------------------------------------------------------------------------------------  
    

@auth_router.post('/auth/register', status_code=status.HTTP_201_CREATED)
async def register(user: schemas.CreateUser, db: Session = Depends(get_db)):
    '''Endpoint to register a user'''
    
    # Check if email already exists in database
    user_email_query = db.query(models.User).filter(models.User.email==user.email).first()
    user_username_query = db.query(models.User).filter(models.User.username==user.username).first()
    
    if user_email_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User with this email already exists')
    
    if user_username_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User with this username already exists')
    
    # Password validation
    if user.password != user.password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')
    
    if not Utils.is_valid_password(password=user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Password must contain at least one uppercase, lowercase, numerical, and special character'
        )
        
    # Perform password hashing
    user.password = Utils.hash_password(user.password)
        
    new_user = models.User(
        username=user.username,
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        profile_pic=None,
    )
    
    # Save user tp database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Verify email
    send_verification_mail(user=new_user)
    
    return {
        'message': f'Check {new_user.email} for a verification link',
    }


@auth_router.get('/email/verify')
async def verify_email(request: Request, db: Session = Depends(get_db)):
    '''Endpoint to verify email'''
    
    # Get query parameter value to extract token
    token = request.url.query.split('=')[-1]
    
    user_id = oauth2.decode_access_token(token).get('user_id')
    user = db.get(models.User, ident=user_id)
    
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Token is invalid')
    
    user.is_verified = True
    db.commit()
    
    return {'message': 'Your account has been verified successfully'}
    

@auth_router.post('/email/reverify')
async def reverify_email(schema: schemas.ReveifyEmail, db: Session = Depends(get_db)):
    '''Endpoint to reverify email'''
    
    user = db.query(models.User).filter(models.User.email == schema.email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User with this email does not exist')
    
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This account has been verified already')
    
    send_verification_mail(user=user)
    return {'message': f'Check {user.email} for a verification link'}


@auth_router.post('/auth/login', status_code=status.HTTP_200_OK, response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    '''
        Endpoint to log in a user with username and password. An access token will be provided as the response.\n
        This token will be a bearer token to be used in request headers in this way:\n
            'Authorization': 'Bearer <token>'\n
        'Authorization' is the key and 'Bearer token' will be the value.
    '''
    
    # Check if username exists in database and perform permission checks
    user = db.query(models.User).filter(models.User.username==user_credentials.username).first()
    permissions.default_permission(user)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
    
    # Verify password with database hash
    if not Utils.verify_password(password=user_credentials.password, hash=user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
    
    # Create access token and pass pata to be encoded into the token
    access_token = oauth2.create_access_token({'user_id': f'{user.id}'})
    
    # Add access token to token table in database
    token = models.Token(
        token=access_token,
        user_id=user.id,
        expires=datetime.fromtimestamp(oauth2.decode_access_token(access_token).get('exp'))
    )
    db.add(token)
    db.commit()
    
    # Return token
    return {'access_token': access_token, 'token_type': 'bearer'}


@auth_router.post('/auth/logout', status_code=status.HTTP_200_OK)
def logout(db: Session = Depends(get_db), user_id: uuid.UUID = Depends(oauth2.get_current_user)):
    '''Endpoint to logout a user'''
    
    token = db.query(models.Token).filter(models.Token.user_id == user_id)
    
    # Delete token from database
    token.delete(synchronize_session=False)
    db.commit()
    
    return {'success': 'Logged out successfully'}
