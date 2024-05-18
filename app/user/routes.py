import os
from pathlib import Path
from typing import List
from secrets import token_hex

from fastapi import APIRouter, UploadFile, File, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app import utils as app_utils
from app.user import auth
from app.database import get_db

from . import models
from . import schemas
from . import oauth2
from . import permissions
from .utils import Utils

user_router = APIRouter(prefix='/user', tags=['Users'])

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


@user_router.put('/email/update', status_code=status.HTTP_200_OK)
def update_email(user_schema: schemas.UpdateEmail, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to update user email'''
    
    permissions.default_permission(current_user)
    
    current_user.is_verified = False
    current_user.email = user_schema.email
    db.commit()
    
    # Re-verify email
    auth.send_verification_mail(user=current_user)
    
    return {'message': f'Email changed successfully. Check {current_user.email} for a verification link.'}


@user_router.put('/password/change', status_code=status.HTTP_200_OK)
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
async def update_profile_picture(profile_pic: UploadFile = File(...), db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to upload user picture'''
    
    permissions.default_permission(current_user)
    
    file_data = await app_utils.upload_file(
        file=profile_pic,
        allowed_extensions=['jpg', 'jpeg', 'png', 'jfif'],
        upload_folder='user',
        new_filename=f'user_pic-{current_user.id}-{token_hex(5)}.jpg'
    )
        
    # TODO: Upload file to database
    
    return file_data


@user_router.delete('/delete', status_code=status.HTTP_200_OK)
def delete_user(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to delete user. This action will render the user's account as inactive'''
    
    permissions.default_permission(current_user)
    
    # Render account as inactive
    current_user.is_active = False
    db.commit()
    
    return {'message': 'User deletion successful'}


# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------


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


@user_router.post('/profile/customer/fetch', status_code=status.HTTP_200_OK, response_model=schemas.CustomerResponse)
def get_customer_profile(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get current logged in user customer profile'''
    
    permissions.is_customer(current_user)
    
    customer = db.query(models.Customer).filter(models.Customer.user_id == current_user.id).first()
    
    return customer


@user_router.put('/profile/customer/update', status_code=status.HTTP_201_CREATED, response_model=schemas.CustomerResponse)
def update_customer_profile(customer_schema: schemas.UpdateCustomer, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for user to update customer profile'''
    
    permissions.is_customer(current_user)
    
    customer_query = db.query(models.Customer).filter(models.Customer.user_id == current_user.id)
    
    customer_query.update(customer_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return customer_query.first()


# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------


@user_router.post('/profile/vendor/add', status_code=status.HTTP_201_CREATED, response_model=schemas.VendorResponse)
def create_vendor_profile(vendor_schema: schemas.CreateVendor, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for user to create vendor profile'''
    
    permissions.is_vendor(current_user)
    
    # Check if customer profile exists
    if db.query(models.Vendor).filter(models.Vendor.user_id == current_user.id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Vendor profile already exists for this user.')
    
    new_vendor = models.Vendor(
        user_id=current_user.id,
        **vendor_schema.model_dump()
    )
    
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    
    return new_vendor


@user_router.post('/profile/vendor/fetch', status_code=status.HTTP_201_CREATED, response_model=schemas.VendorResponse)
def get_vendor_profile(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get current user vendor profile'''
    
    permissions.is_vendor(current_user)
    
    vendor = db.query(models.Vendor).filter(models.Vendor.user_id == current_user.id).first()
    
    return vendor


@user_router.put('/profile/vendor/update', status_code=status.HTTP_201_CREATED, response_model=schemas.VendorResponse)
def update_vendor_profile(vendor_schema: schemas.UpdateVendor, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for user to update vendor profile'''
    
    permissions.is_vendor(current_user)
    
    vendor_query = db.query(models.Vendor).filter(models.Vendor.user_id == current_user.id)
    
    vendor_query.update(vendor_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return vendor_query.first()


@user_router.put('/profile/vendor/business-pic/update', status_code=status.HTTP_201_CREATED)
async def update_vendor_picture(business_pic: UploadFile, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to update vendor picture'''
    
    permissions.is_vendor(current_user)
    
    file_data = await app_utils.upload_file(
        file=business_pic,
        allowed_extensions=['jpg', 'jpeg', 'png', 'jfif'],
        upload_folder='vendor',
        new_filename=f'vendor_pic-{current_user.id}-{token_hex(5)}.jpg'
    )
        
    # TODO: Upload file to database
    
    return file_data
    