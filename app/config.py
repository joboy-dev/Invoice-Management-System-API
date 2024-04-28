import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Settings(BaseSettings):
    '''Settings configuration class'''
    
    # debug: bool = True if os.getenv('DEBUG') == 'True' else False
    debug: str 
    
    secret_key: str
    algorithm: str
    access_token_expire_hours: int

    hostname: str
    name: str
    user: str
    password: str 
    port: int

    my_email: str
    my_password: str
    
    # In case thay are too many env variables, do this below:
    class Config:
        env_file = '.env'

settings = Settings()


# debug: bool = True if os.getenv('DEBUG') == 'True' else False
    
#     secret_key: str = os.getenv('SECRET_KEY')
#     algorithm: str = os.getenv('ALGORITHM')
#     access_token_expire_hours: int = os.getenv('ACCESS_TOKEN_EXPIRE_HOURS')

#     database_hostname: str = os.getenv('HOSTNAME')
#     database_name: str = os.getenv('DATABASE')
#     database_username: str= os.getenv('USER')
#     database_password: str= os.getenv('PASSWORD')
#     database_port: str= os.getenv('PORT')

#     email: str = os.getenv('MY_EMAIL')
#     passwod: str = os.getenv('MY_PASSWORD') 