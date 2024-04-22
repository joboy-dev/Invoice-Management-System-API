from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from .models import User, UserModel
from app.database import get_db

user_router = APIRouter()

@user_router.post('/users/register', status_code=status.HTTP_201_CREATED, response_model=UserModel)
async def register(user: UserModel, db: Session = Depends(get_db)):
    '''Endpoint to register a user'''
    
    return {'data': 'Wow'}
