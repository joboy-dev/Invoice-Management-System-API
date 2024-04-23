import re
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Utils:
    '''Utility functions'''
    
    @staticmethod
    def is_valid_email(email):
        '''Function to check if email is valid'''
        
        # Regular expression for a valid email address
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_regex, email):
            return True
        else:
            return False
        
    @staticmethod
    def is_valid_password(password: str):
        '''Function to check if password is valid'''
        
        # Regular expression for a valid password
        # Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one digit, and one special character.
        password_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        
        if re.match(password_regex, password):
            return True
        else:
            return False
        
    @staticmethod
    def hash_password(password: str):
        '''Function to hash a password'''
        
        hashed_password = pwd_context.hash(secret=password)     
        return hashed_password   
    
    @staticmethod
    def is_password_matched(password: str, hash):
        '''Function to verify a hashed password'''
        
        return pwd_context.verify(secret=password, hash=hash) 