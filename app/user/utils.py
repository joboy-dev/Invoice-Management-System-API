import os
from pathlib import Path
import re, smtplib
from dotenv import load_dotenv
from fastapi import HTTPException
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class Utils:
    '''Utility functions'''
    
    @staticmethod
    def is_valid_email(email) -> bool:
        '''Function to check if email is valid'''
        
        # Regular expression for a valid email address
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_regex, email):
            return True
        else:
            return False
        
    @staticmethod
    def is_valid_password(password: str) -> bool:
        '''Function to check if password is valid'''
        
        # Regular expression for a valid password
        # Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one digit, and one special character.
        password_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        
        if re.match(password_regex, password):
            return True
        else:
            return False
        
    @staticmethod
    def hash_password(password: str) -> str:
        '''Function to hash a password'''
        
        hashed_password = pwd_context.hash(secret=password)     
        return hashed_password   
    
    @staticmethod
    def verify_password(password: str, hash: str) -> bool:
        '''Function to verify a hashed password'''
        
        return pwd_context.verify(secret=password, hash=hash) 
    
    @staticmethod
    def send_email(data: dict):
        '''
        Function to send email to a user;s email.\n
        In the data dictionary, the following fields showuld be provided:
            * subject - Subject of the email
            * body - The content the email should contain
            * email - The email the verification email should be sent to
        '''
        
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as conn:
                conn.starttls()
                conn.login(user=settings.my_email, password=settings.my_password)
                conn.sendmail(
                    from_addr=settings.my_email,
                    to_addrs=data['email'],
                    msg=f"Subject:{data['subject']}\n\n{data['body']}"
                )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f'An exception occured. [{e}]')
        