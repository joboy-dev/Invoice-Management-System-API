from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel
import sqlalchemy as sa
from sqlalchemy.sql.expression import text

from app.database import Base

class Role(str, Enum):
    '''Role choices for user model'''
    
    admin = 'admin'
    employee = 'employee'
    manager = 'manager'
    customer = 'customer'
    
    
class User(Base):
    '''Users model'''
    
    __tablename__ = 'users'
    
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = sa.Column(sa.String(length=128), unique=True, nullable=False)
    password = sa.Column(sa.String, nullable=False)
    first_name = sa.Column(sa.String(length=128), nullable=False)
    last_name = sa.Column(sa.String(length=128), nullable=False)
    profile_pic = sa.Column(sa.String, nullable=True)
    role = sa.Column(sa.Enum(Role), nullable=False, server_default=Role.customer.value) 
    is_verified = sa.Column(sa.Boolean, nullable=False, server_default='False')
    is_active = sa.Column(sa.Boolean, nullable=False, server_default='True')
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    
class Customer(Base):
    '''Customers model'''
    
    __tablename__ = 'customers'
    
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4)
    phone_number = sa.Column(sa.String, nullable=False)
    billing_address = sa.Column(sa.String, nullable=False)
    