from fastapi import HTTPException, status
from app.user import models

def forbidden_exception(message: str, code: int=status.HTTP_403_FORBIDDEN):
    raise HTTPException(status_code=code, detail=message)

# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------

def default_permission(user: models.User):
    '''Permission to check if the logged in user is active and verified. This is the default general permission'''
    
    if not user.is_active:
        raise forbidden_exception(message='Access denied as you are not an active user.')
    if not user.is_verified:
        raise forbidden_exception(message='Access denied as you are not a verified user. Verify your email address.')
    
    
def is_vendor(user: models.User):
    '''Permission to check if the logged in user is an seller'''
    
    default_permission(user)
    
    if not user.role == 'vendor':
        raise forbidden_exception(message='Access denied as you are not a vendor.')
    

def is_customer(user: models.User):
    '''Permission to check if the logged in user is a customer'''
    
    default_permission(user)
    
    if not user.role == 'customer':
        raise forbidden_exception(message='Access denied as you are not a customer.')
