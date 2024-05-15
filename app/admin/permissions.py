from app.user import models as user_models, permissions as user_permessions

def is_admin(user: user_models.User):
    '''Permission to check if the logged in user is an admin'''
    
    user_permessions.default_permission(user)
    
    if not user.role == 'admin':
        raise user_permessions.forbidden_exception(message='Access denied as you are not an admin.')