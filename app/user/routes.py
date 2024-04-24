from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from . import models
from . import schemas

from app.database import get_db

user_router = APIRouter(prefix='/users', tags=['Users'])

@user_router.get('', status_code=status.HTTP_200_OK, response_model=List[schemas.UserResponse])
def get_all_users(first_name: str = '', last_name: str = '', db: Session = Depends(get_db)):
    '''Endpoint to search for users with first name and last name'''
    
    users = db.query(models.User).filter(
        models.User.first_name.ilike(f'%{first_name}%'), 
        models.User.last_name.ilike(f'%{last_name}%')
    )
    
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No users found')
    
    return users


@user_router.get('/{id}/fetch', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def get_user_by_id(id, db: Session = Depends(get_db)):
    '''Endpoint to get a user by id'''
    
    user = db.get(models.User, ident=id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    return user


@user_router.put('/{id}/update', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def update_user_details(id, user_schema: schemas.UpdateDetails, db: Session = Depends(get_db)):
    '''Endpoint to update user details'''
    
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    user_query.update(user_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return user_query.first()


@user_router.put('/{id}/email/update', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def update_email(id, user_schema: schemas.UpdateEmail, db: Session = Depends(get_db)):
    '''Endpoint to update user email'''
    
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    # Verify email
    
    user_query.update(user_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return user_query.first()


@user_router.put('/{id}/profile-picture/update', status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def update_profile_picture(id, user_schema: schemas.UploadProfilePicture, db: Session = Depends(get_db)):
    '''Endpoint to upload user picture'''
    
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    user_query.update(user_schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return user_query.first()


@user_router.post('/{id}/delete', status_code=status.HTTP_200_OK)
def delete_user(id, db: Session = Depends(get_db)):
    '''Endpoint to delete user. This action will render the user's account as inactive'''
    
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User does not exist')
    
    # Render account as inactive
    user.is_active = False
    db.commit()
    
    return {'message': 'User deletion successful'}
        