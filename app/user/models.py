from enum import Enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

from app.database import Base

class Role(str, Enum):
    '''Role choices for user model'''
    
    admin = "admin"
    customer = "customer"
    vendor = "vendor"
    
    
class User(Base):
    '''Users model'''
    
    __tablename__ = 'users'
    
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    username = sa.Column(sa.String(length=128), unique=True, nullable=False, index=True)
    email = sa.Column(sa.String(length=128), unique=True, nullable=False, index=True)
    password = sa.Column(sa.String, nullable=False)
    first_name = sa.Column(sa.String(length=128), nullable=False)
    last_name = sa.Column(sa.String(length=128), nullable=False)
    profile_pic = sa.Column(sa.String, nullable=True)
    role = sa.Column(sa.Enum(Role), nullable=False, server_default=Role.customer.value) 
    is_verified = sa.Column(sa.Boolean, nullable=False, server_default='False')
    is_active = sa.Column(sa.Boolean, nullable=False, server_default='True')
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    tokens = relationship('Token', back_populates='user')
    customer = relationship('Customer', back_populates='user', uselist=False)
    vendor = relationship('Vendor', back_populates='user', uselist=False)
    

class Token(Base):
    '''Tokens model'''
    
    __tablename__ = 'tokens'
    
    token = sa.Column(sa.String, unique=True, primary_key=True, nullable=False, index=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    expires = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False)
    
    user_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey(column='users.id', ondelete='CASCADE'), nullable=False)
    user = relationship('User', back_populates='tokens')
    
    
class Customer(Base):
    '''Customers model'''
    
    __tablename__ = 'customers'
    
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    phone_number = sa.Column(sa.String(length=11), nullable=False)
    billing_address = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    user_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    user = relationship('User', back_populates='customer')
    invoices = relationship('Invoice', back_populates='customer')
    payments = relationship('Payment', back_populates='customer')
    

class Vendor(Base):
    '''Vendors model'''
    
    __tablename__ = 'vendors'
    
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    phone_number = sa.Column(sa.String(length=11), nullable=False)
    business_name = sa.Column(sa.String, nullable=False)
    business_pic = sa.Column(sa.String, nullable=True)
    address = sa.Column(sa.String, nullable=False)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    user_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    user = relationship('User', back_populates='vendor')
    products = relationship('Product', back_populates='vendor')
    invoices = relationship('Invoice', back_populates='vendor')
    payments = relationship('Payment', back_populates='customer')
    
    