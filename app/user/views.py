from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from .models import User
from .schemas import UserSchema, CustomerSchema

from app.database import get_db

user_router = APIRouter(prefix='/users')

@user_router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserSchema)
def register(user: UserSchema, db: Session = Depends(get_db)):
    '''Endpoint to register a user'''
    
    
    return {'data': 'Wow'}
