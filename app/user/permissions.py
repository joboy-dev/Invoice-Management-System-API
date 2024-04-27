from fastapi import HTTPException, status
from app.user import models

def exception(message: str, code: int=status.HTTP_403_FORBIDDEN):
    raise HTTPException(status_code=code, detail=message)

# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------

def default_permission(user: models.User):
    '''Permission to check if the logged in user is active and verified. This is the default general permission'''
    
    if not user.is_active:
        raise exception(message='Access denied as you are not an active user.')
    if not user.is_verified:
        raise exception(message='Access denied as you are not a verified user. Verify your email address.')
    

def is_staff(user: models.User):
    '''Permission to check if the logged in user is an employee or admin'''
    
    default_permission(user)
    
    if not (user.role == 'employee' or user.role == 'admin'):
        raise exception(message='Access denied as you are not a staff member.')
    
    
def is_admin(user: models.User):
    '''Permission to check if the logged in user is an admin'''
    
    default_permission(user)
    
    if not user.role == 'admin':
        raise exception(message='Access denied as you are not an admin.')
    
    
def is_employee(user: models.User):
    '''Permission to check if the logged in user is an employee'''
    
    default_permission(user)
    
    if not user.role == 'employee':
        raise exception(message='Access denied as you are not an admin.')
    

def is_customer(user: models.User):
    '''Permission to check if the logged in user is a customer'''
    
    default_permission(user)
    
    if not user.role == 'customer':
        raise exception(message='Access denied as you are not a customer.')
