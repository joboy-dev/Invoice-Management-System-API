import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Settings(BaseSettings):
    '''Settings configuration class'''
    
    debug: bool = True if os.getenv('DEBUG') == 'True' else False
    
    secret_key: str = os.getenv('SECRET_KEY')
    algorithm: str = os.getenv('ALGORITHM')
    access_token_expire_hours: int = os.getenv('ACCESS_TOKEN_EXPIRE_HOURS')

    hostname: str = os.getenv('HOSTNAME')
    name: str = os.getenv('DATABASE')
    user: str= os.getenv('USER')
    password: str= os.getenv('PASSWORD')
    port: str= os.getenv('PORT')
    
    postgres_dev_url: str = os.getenv('POSTGRES_DEV_URL')
    postgres_prod_url: str = os.getenv('POSTGRES_PROD_URL')

    my_email: str = os.getenv('MY_EMAIL')
    my_password: str = os.getenv('MY_PASSWORD') 
    
    # In case thay are too many env variables, do this below:
    # class Config:
    #     env_file = '.env'

settings = Settings()