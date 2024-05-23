from typing import List
import uuid
from fastapi import APIRouter, File, HTTPException, status, Depends, UploadFile
from sqlalchemy.orm import Session

from app.user import models as user_models, schemas as user_schemas, oauth2
from app.database import get_db
from app.user.utils import Utils
from app.utils import upload_file
from . import permissions, schemas

admin_user_router = APIRouter(prefix='/admin/users', tags=['Admin [User]'])

@admin_user_router.get('', status_code=status.HTTP_200_OK, response_model=List[user_schemas.UserResponse])
def get_all_users(limit: int = 0, skip: int = 0, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Admin endpoint to get all users'''
    
    permissions.is_admin(current_user)
    
    users = db.query(user_models.User).limit(limit).offset(skip).all()
    return users


@admin_user_router.get('/{user_id}', status_code=status.HTTP_200_OK, response_model=List[user_schemas.UserResponse])
def get_user_by_id(user_id: uuid.UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Admin endpoint to get a single user'''
    
    permissions.is_admin(current_user)
    
    user = db.get(user_models.User, ident=user_id)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    return user


@admin_user_router.post('/add', status_code=status.HTTP_201_CREATED, response_model=user_schemas.UserResponse)
def add_new_user(schema: user_schemas.CreateUser, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Admin endpoint to add a new user'''
    
    permissions.is_admin(current_user)
    
    # Check if email already exists in database
    user_email_query = db.query(user_models.User).filter(user_models.User.email==schema.email).first()
    user_username_query = db.query(user_models.User).filter(user_models.User.username==schema.username).first()
    
    if user_email_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User with this email already exists')
    
    if user_username_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User with this username already exists')
    
    # Password validation
    if schema.password != schema.password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match')
        
    if not Utils.is_valid_password(password=schema.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail='Password must contain at least one uppercase, lowercase, numerical, and special character'
        )
        
    # Perform password hashing
    schema.password = Utils.hash_password(schema.password)
        
    new_user = user_models.User(
        username=schema.username,
        email=schema.email,
        password=schema.password,
        first_name=schema.first_name,
        last_name=schema.last_name,
        role=schema.role,
        profile_pic=None,
        is_verified=True,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@admin_user_router.put('/{user_id}/update', status_code=status.HTTP_200_OK, response_model=user_schemas.UserResponse)
def update_user(user_id: uuid.UUID, schema: schemas.AdminUserBase, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Admin endpoint to update a user'''
    
    permissions.is_admin(current_user)
        
    # Perform password hashing
    schema.password = Utils.hash_password(schema.password)
    
    user_query = db.query(user_models.User).filter(user_models.User.id == user_id)
    user = user_query.first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    user_query.update(schema.model_dump(), synchronize_session=False)

    db.commit()
    
    return user


@admin_user_router.put('/{user_id}/profile-picture/update', status_code=status.HTTP_200_OK)
async def update_user_profile_picture(user_id: uuid.UUID, profile_pic: UploadFile = File(...), db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to upload user picture'''
    
    permissions.is_admin(current_user)
    
    user = db.get(user_models.User, ident=user_id)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    file_data = await upload_file(
        file=profile_pic,
        allowed_extensions=['jpg', 'jpeg', 'png', 'jfif'],
        upload_folder='user',
        model_id=user.id
    )
        
    # Upload download url to database
    user.profile_pic = file_data['download_url']
    db.commit()
    
    return file_data


@admin_user_router.delete('/{user_id}/remove', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Admin endpoint to remove a user'''
    
    permissions.is_admin(current_user)
    
    user = db.get(user_models.User, ident=user_id)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    db.delete(user)
    db.commit()


# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------


@admin_user_router.post('/customer/add', status_code=status.HTTP_201_CREATED, response_model=user_schemas.CustomerResponse)
def create_customer_profile(customer_schema: schemas.AdminCustomerBase, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for admin to create customer profile'''
    
    permissions.is_admin(current_user)
    
    # Check if customer profile exists
    if db.query(user_models.Customer).filter(user_models.Customer.user_id == customer_schema.user_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Customer profile already exists for this user.')
    
    # Check if user exists
    if not db.query(user_models.User).filter(user_models.User.id == customer_schema.user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')
    
    new_customer = user_models.Customer(
        **customer_schema.model_dump()
    )
    
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    return new_customer


@admin_user_router.post('/customer/{customer_id}/fetch', status_code=status.HTTP_200_OK, response_model=user_schemas.CustomerResponse)
def get_customer_profile(customer_id: uuid.UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get customer profile'''
    
    permissions.is_admin(current_user)
    
    customer = db.query(user_models.Customer).filter(user_models.Customer.id == customer_id).first()
        
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Customer profile not found.')
    
    return customer


@admin_user_router.put('/customer/{customer_id}//update', status_code=status.HTTP_200_OK, response_model=user_schemas.CustomerResponse)
def update_customer_profile(customer_id: uuid.UUID, customer_schema: schemas.AdminCustomerBase, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for admin to update customer profile'''
    
    permissions.is_admin(current_user)
    
    customer_query = db.query(user_models.Customer).filter(user_models.Customer.id == customer_id)
    customer = customer_query.first()
    
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Customer profile not found.')
    
    customer_query.update(customer_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return customer


@admin_user_router.delete('/customer/{customer_id}/delete', status_code=status.HTTP_204_NO_CONTENT)
def delete_customer_profile(customer_id: uuid.UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for admin to delete customer profile'''
    
    permissions.is_admin(current_user)
    
    customer_query = db.query(user_models.Customer).filter(user_models.Customer.id == customer_id)
    customer = customer_query.first()
    
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Customer profile not found.')
    
    customer_query.delete(synchronize_session=False)
    db.commit()


# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------


@admin_user_router.post('/vendor/add', status_code=status.HTTP_201_CREATED, response_model=user_schemas.VendorResponse)
def create_vendor_profile(vendor_schema: schemas.AdminVendorBase, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for admin to create vendor profile'''
    
    permissions.is_admin(current_user)
    
    # Check if customer profile exists
    if db.query(user_models.Vendor).filter(user_models.Vendor.user_id == current_user.id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Vendor profile already exists for this user.')
    
    # Check if user exists
    if not db.query(user_models.User).filter(user_models.User.id == vendor_schema.user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')
    
    new_vendor = user_models.Vendor(
        **vendor_schema.model_dump()
    )
    
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    
    return new_vendor


@admin_user_router.post('/vendor/{vendor_id}/fetch', status_code=status.HTTP_200_OK, response_model=user_schemas.VendorResponse)
def get_vendor_profile(vendor_id: uuid.UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get vendor profile'''
    
    permissions.is_admin(current_user)
    
    vendor = db.query(user_models.Vendor).filter(user_models.Vendor.id == vendor_id).first()
    
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vendor profile not found.')
    
    return vendor


@admin_user_router.put('/vendor/{vendor_id}/update', status_code=status.HTTP_200_OK, response_model=user_schemas.VendorResponse)
def update_vendor_profile(vendor_id: uuid.UUID, vendor_schema: user_schemas.UpdateVendor, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for user to update vendor profile'''
    
    permissions.is_admin(current_user)
    
    vendor_query = db.query(user_models.Vendor).filter(user_models.Vendor.id == vendor_id)
    vendor = vendor_query.first()
    
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vendor profile not found.')
    
    vendor_query.update(vendor_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return vendor


@admin_user_router.put('/vendor/{vendor_id}/business-pic/update', status_code=status.HTTP_200_OK)
async def update_vendor_picture(vendor_id: uuid.UUID, business_pic: UploadFile, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to update vendor picture'''
    
    permissions.is_admin(current_user)
    
    vendor = db.query(user_models.Vendor).filter(user_models.Vendor.id == vendor_id).first()
    
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vendor profile not found.')
    
    file_data = await upload_file(
        file=business_pic,
        allowed_extensions=['jpg', 'jpeg', 'png', 'jfif'],
        upload_folder='vendor',
        model_id=vendor.id
    )
        
    # Upload download url to database
    vendor.business_pic = file_data['download_url']
    db.commit()
    
    return file_data


@admin_user_router.delete('/vendor/{vendor}/delete', status_code=status.HTTP_204_NO_CONTENT)
def delete_vendor_profile(vendor_id: uuid.UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for admin to delete vendor profile'''
    
    permissions.is_admin(current_user)
    
    vendor_query = db.query(user_models.Vendor).filter(user_models.Vendor.id == vendor_id)
    vendor = vendor_query.first()
    
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vendor profile not found.')
    
    vendor_query.delete(synchronize_session=False)
    db.commit()
    