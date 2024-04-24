from datetime import datetime
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app.user.utils import Utils
from app.user.oauth2 import create_access_token

from . import models
from . import schemas

from app.database import get_db

auth_router = APIRouter(tags=['Authentication'])

@auth_router.post('/register', status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def register(user: schemas.CreateUser, db: Session = Depends(get_db)):
    '''Endpoint to register a user'''
    
    # Check if email already exists in database
    user_email_query = db.query(models.User).filter(models.User.email==user.email).first()
    
    if user_email_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User with this email already exists')
    
    # Password validation
    if user.password != user.password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')
    
    if not Utils.is_valid_password(password=user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Password must contain at least one uppercase, lowercase, numerical, and special character'
        )
        
    # Verify email
        
    # Perform password hashing
    user.password = Utils.hash_password(user.password)
        
    new_user = models.User(
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        profile_pic=None,
        is_verified= False,
        is_active=True,
        created_at=datetime.now()
    )
    
    # Save user tp database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@auth_router.post('/login', status_code=status.HTTP_200_OK)
def login(user_schema: schemas.LoginUser, db: Session = Depends(get_db)):
    '''
        Endpoint to log in a user with email and password. An access token will be provided as the response.\n
        This token will be a bearer token to be used in request headers in this way:\n
            headers = {\n
                'Authorization': 'Bearer token'\n
            }
    '''
    
    # Check if email exists in database
    user = db.query(models.User).filter(models.User.email==user_schema.email).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid credentials email')
    
    # Verify password
    if not Utils.is_password_matched(password=user_schema.password, hash=user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid credentials pword')
    
    # Create access token and pass pata to be encoded into the token
    access_token = create_access_token({'user_id': f'{user.id}'})
    
    # Return token
    return {'access_token': access_token, 'token_type': 'bearer'}
