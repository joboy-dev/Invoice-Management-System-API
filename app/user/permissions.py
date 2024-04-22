from fastapi import HTTPException, status

from app.user.models import User

class UserPermissions:
    '''Permission class for user permissions'''
    
    @staticmethod
    def is_admin(fn):
        '''Permission function to check if the current logged in user is an admin'''
        
        def wrapper(user: User):
            '''Wrapper function'''
            
            if user.role == 'admin':
                return fn(user)
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied as you are not an admin.')
        
        return wrapper
    
    @staticmethod
    def is_employee(fn):
        '''Permission function to check if the current logged in user is an employee'''
        
        def wrapper(user: User):
            '''Wrapper function'''
            
            if user.role == 'employee':
                return fn(user)
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied as you are not an employee.')
        
        return wrapper