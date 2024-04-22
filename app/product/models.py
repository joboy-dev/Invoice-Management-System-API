from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel
import sqlalchemy as sa

from app.database import Base

class Product(Base):
    '''Products model'''
    
    __tablename__ = 'products'
    
    id = sa.Column(sa.UUID, primary_key=True, server_default=f'{uuid4()}')
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=False)
    unit_price = sa.Column(sa.Float, nullable=False, server_default='0.00')
    

class ProductModel(BaseModel):
    '''Product pydantic model'''
    
    id = uuid4
    name: str
    description: str
    unit_price: float = 0.00
    