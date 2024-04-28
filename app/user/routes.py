import os
from pathlib import Path
import datetime as dt
from typing import List
import uuid
from secrets import token_hex

from fastapi import APIRouter, UploadFile, File, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app.user import auth
from app.database import get_db

from . import models
from . import schemas
from . import oauth2
from . import permissions
from .utils import Utils

user_router = APIRouter(prefix='/user', tags=['Users'])

@user_router.get('', status_code=status.HTTP_200_OK, response_model=List[schemas.UserResponse])
def get_all_users(first_name: str = '', last_name: str = '', username: str = '', db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get users and search for users with username, first name or last name'''
    
    permissions.is_staff(current_user)
        
    users = db.query(models.User).filter(
        models.User.username.ilike(f'%{username}%'), 
        models.User.first_name.ilike(f'%{first_name}%'), 
        models.User.last_name.ilike(f'%{last_name}%')
    )
    
    return users


@user_router.get('/profile', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def get_user_details(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get logged in user details'''
    
    permissions.default_permission(current_user)
    return current_user


@user_router.get('/{id}/fetch', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def get_user_by_id(id, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get a user by id'''
    
    permissions.default_permission(current_user)
    
    searched_user = db.get(models.User, ident=id)
    
    if not searched_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    return searched_user


@user_router.put('/profile/update', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def update_user_details(user_schema: schemas.UpdateDetails, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to update user details'''
    
    permissions.default_permission(current_user)
    
    user_query = db.query(models.User).filter(models.User.id == current_user.id)
    user_query.update(user_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return user_query.first()


@user_router.post('/email/update', status_code=status.HTTP_200_OK)
def update_email(user_schema: schemas.UpdateEmail, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to update user email'''
    
    permissions.default_permission(current_user)
    
    current_user.is_verified = False
    current_user.email = user_schema.email
    db.commit()
    
    # Re-verify email
    auth.send_verification_mail(user=current_user)
    
    return {'message': f'Email changed successfully. Check {current_user.email} for a verification link.'}


@user_router.post('/password/change', status_code=status.HTTP_200_OK)
def change_password(user_schema: schemas.ChangePassword, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to change user password'''
    
    permissions.default_permission(current_user)
    
    # Reauthenticate the user and perform additional checks
    if not db.query(models.User).filter(models.User.email == user_schema.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid credentials. Check your email or old password')
    
    if not Utils.verify_password(user_schema.old_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid credentials. Check your email or old password')
    
    if user_schema.new_password != user_schema.password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='New password does not match')
    
    if user_schema.old_password == user_schema.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Old password and new password cannot be the same')
    
    current_user.password = Utils.hash_password(user_schema.new_password)
    db.commit()
    
    return {'message': 'Password changed successfully'}


@user_router.put('/profile-picture/update', status_code=status.HTTP_200_OK)
async def update_profile_picture(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to upload user picture'''
    
    permissions.default_permission(current_user)
    
    # Check against invalid extensions
    file_name = file.filename.lower()
    file_extension = file_name.split('.')[-1]
    
    if file_extension not in ['jpg', 'jpeg', 'jfif', 'png']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid file format')
    
    # Create file storage path
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads', 'user')
    
    if not os.path.exists(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)
    
    # Generate a new file name
    new_filename = f'user_pic-{current_user.id}-{token_hex(5)}.jpg'
    SAVE_FILE_DIR = os.path.join(UPLOAD_DIR, new_filename)
    
    with open(SAVE_FILE_DIR, 'wb') as f:
        content = await file.read()
        f.write(content)
        
    # TODO: Upload file to database
    
    
    return {
        'filename': new_filename,
        'filepath': SAVE_FILE_DIR
    }


@user_router.delete('/delete', status_code=status.HTTP_200_OK)
def delete_user(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to delete user. This action will render the user's account as inactive'''
    
    permissions.default_permission(current_user)
    
    # Render account as inactive
    current_user.is_active = False
    db.commit()
    
    return {'message': 'User deletion successful'}


@user_router.post('/profile/customer/add', status_code=status.HTTP_201_CREATED, response_model=schemas.CustomerResponse)
def create_customer_profile(customer: schemas.CreateCustomer, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for user to create customer profile'''
    
    permissions.is_customer(current_user)
    
    # Check if customer profile exists
    if db.query(models.Customer).filter(models.Customer.user_id == current_user.id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Customer profile already exists for this user.')
    
    new_customer = models.Customer(
        phone_number=customer.phone_number,
        billing_address=customer.billing_address,
        user_id=current_user.id
    )
    
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    return new_customer


@user_router.patch('/profile/customer/update', status_code=status.HTTP_201_CREATED, response_model=schemas.CustomerResponse)
def update_customer_profile(customer_schema: schemas.UpdateCustomer, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for user to update customer profile'''
    
    permissions.is_customer(current_user)
    
    customer_query = db.query(models.Customer).filter(models.Customer.user_id == current_user.id)
    
    customer_query.update(customer_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return customer_query.first()
    