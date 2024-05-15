from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.user import models as user_models, schemas as user_schemas, oauth2
from app.database import get_db
from . import permissions

admin_user_router = APIRouter(prefix='/admin/users', tags=['Admin [User]'])

@admin_user_router.get('', status_code=status.HTTP_200_OK, response_model=List[user_schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Admin endpoint to get all users'''
    
    permissions.is_admin(current_user)
    users = db.query(user_models.User).all()
    return users