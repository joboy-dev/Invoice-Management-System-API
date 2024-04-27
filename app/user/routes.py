from typing import List
import uuid
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app.user import auth

from . import models
from . import schemas
from . import oauth2
from . import permissions
from .utils import Utils

from app.database import get_db

user_router = APIRouter(prefix='/user', tags=['Users'])

@user_router.get('', status_code=status.HTTP_200_OK, response_model=List[schemas.UserResponse])
def get_all_users(first_name: str = '', last_name: str = '', username: str = '', db: Session = Depends(get_db), user_id: uuid.UUID = Depends(oauth2.get_current_user)):
    '''Endpoint to get users and search for users with username, first name or last name'''
    
    user = db.get(models.User, ident=user_id)
    permissions.is_staff(user)
        
    users = db.query(models.User).filter(
        models.User.username.ilike(f'%{username}%'), 
        models.User.first_name.ilike(f'%{first_name}%'), 
        models.User.last_name.ilike(f'%{last_name}%')
    )
    
    return users


@user_router.get('/profile', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def get_user_details(db: Session = Depends(get_db), user_id: uuid.UUID = Depends(oauth2.get_current_user)):
    '''Endpoint to get logged in user details'''
    
    user = db.get(models.User, ident=user_id)
    permissions.default_permission(user)
    
    user = db.get(models.User, ident=user_id)
    return user


@user_router.get('/{id}/fetch', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def get_user_by_id(id, db: Session = Depends(get_db), user_id: uuid.UUID = Depends(oauth2.get_current_user)):
    '''Endpoint to get a user by id'''
    
    user = db.get(models.User, ident=user_id)
    permissions.default_permission(user)
    
    searched_user = db.get(models.User, ident=id)
    
    if not searched_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    return searched_user


@user_router.put('/profile/update', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def update_user_details(user_schema: schemas.UpdateDetails, db: Session = Depends(get_db), user_id: uuid.UUID = Depends(oauth2.get_current_user)):
    '''Endpoint to update user details'''
    
    user_query = db.query(models.User).filter(models.User.id == user_id)
    permissions.default_permission(user_query.first())
    
    user_query.update(user_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return user_query.first()


@user_router.put('/email/update', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
async def update_email(user_schema: schemas.UpdateEmail, db: Session = Depends(get_db), user_id: uuid.UUID = Depends(oauth2.get_current_user)):
    '''Endpoint to update user email'''
    
    user_query = db.query(models.User).filter(models.User.id == user_id)
    user = user_query.first()
    permissions.default_permission(user)
    
    user.is_verified = False
    db.commit()
    
    user_query.update(user_schema.model_dump(), synchronize_session=False)
    
    # Re-verify email
    auth.send_verification_mail(user=user)
    
    user.is_verified = True
    db.commit()
    
    return user_query.first()


@user_router.post('/password/change', status_code=status.HTTP_200_OK)
def change_password(user_schema: schemas.ChangePassword, db: Session = Depends(get_db), user_id: uuid.UUID = Depends(oauth2.get_current_user)):
    '''Endpoint to change user password'''
    
    user_query = db.query(models.User).filter(models.User.id == user_id)
    user = user_query.first()
    permissions.default_permission(user)
    
    # Reauthenticate the user and perform additional checks
    if not db.query(models.User).filter(models.User.email == user_schema.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid credentials. Check your email or old password')
    
    if not Utils.verify_password(user_schema.old_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid credentials. Check your email or old password')
    
    if user_schema.new_password != user_schema.password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='New password does not match')
    
    if user_schema.old_password == user_schema.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Old password and new password cannot be the same')
    
    user.password = Utils.hash_password(user_schema.new_password)
    db.commit()
    
    return {'message': 'Password changed successfully'}


@user_router.put('/profile-picture/update', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def update_profile_picture(user_schema: schemas.UploadProfilePicture, db: Session = Depends(get_db), user_id: uuid.UUID = Depends(oauth2.get_current_user)):
    '''Endpoint to upload user picture'''
    
    user_query = db.query(models.User).filter(models.User.id == user_id)
    permissions.default_permission(user_query.first())
    
    user_query.update(user_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return user_query.first()


@user_router.post('/delete', status_code=status.HTTP_200_OK)
def delete_user(db: Session = Depends(get_db), user_id: uuid.UUID = Depends(oauth2.get_current_user)):
    '''Endpoint to delete user. This action will render the user's account as inactive'''
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    permissions.default_permission(user)
    
    # Render account as inactive
    user.is_active = False
    db.commit()
    
    return {'message': 'User deletion successful'}


@user_router.post('/profile/customer/add', status_code=status.HTTP_201_CREATED, response_model=schemas.CustomerResponse)
def create_customer_profile(customer: schemas.CreateCustomer, db: Session = Depends(get_db), user_id: uuid.UUID = Depends(oauth2.get_current_user)):
    '''Endpoint for user to create customer profile'''
    
    user = db.get(models.User, ident=user_id)
    permissions.is_customer(user)
    
    new_customer = models.Customer(
        phone_number=customer.phone_number,
        billing_address=customer.billing_address,
        user_id=user_id
    )
    
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    return new_customer


@user_router.patch('/profile/customer/update', status_code=status.HTTP_201_CREATED, response_model=schemas.CustomerResponse)
def update_customer_profile(customer_schema: schemas.UpdateCustomer, db: Session = Depends(get_db), user_id: uuid.UUID = Depends(oauth2.get_current_user)):
    '''Endpoint for user to update customer profile'''
    
    user = db.get(models.User, ident=user_id)
    permissions.is_customer(user)
    
    customer_query = db.query(models.Customer).filter(models.Customer.user_id == user_id)
    
    customer_query.update(customer_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return customer_query.first()
    