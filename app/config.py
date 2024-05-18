from pydantic_settings import BaseSettings

from app.utils import get_value_from_env

class Settings(BaseSettings):
    '''Settings configuration class'''
    
    debug: bool = True if get_value_from_env('DEBUG') == 'True' else False
    
    secret_key: str = get_value_from_env('SECRET_KEY')
    algorithm: str = get_value_from_env('ALGORITHM')
    access_token_expire_hours: int = get_value_from_env('ACCESS_TOKEN_EXPIRE_HOURS')

    hostname: str = get_value_from_env('HOSTNAME')
    name: str = get_value_from_env('DATABASE')
    user: str= get_value_from_env('USER')
    password: str= get_value_from_env('PASSWORD')
    port: str= get_value_from_env('PORT')
    
    postgres_dev_url: str = get_value_from_env('POSTGRES_DEV_URL')
    postgres_prod_url: str = get_value_from_env('POSTGRES_PROD_URL')

    my_email: str = get_value_from_env('MY_EMAIL')
    my_password: str = get_value_from_env('MY_PASSWORD') 
    
    # In case thay are too many env variables, do this below:
    # class Config:
    #     env_file = '.env'

settings = Settings()