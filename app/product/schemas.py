import uuid
from pydantic import BaseModel

from app.user import schemas

class ProductBase(BaseModel):
    '''Products pydantic base schema'''
    
    name: str
    description: str
    unit_price: float = 0.00
    

class ProductResponse(ProductBase):
    '''Products pydantic base response schema'''
    
    id: uuid.UUID
    vendor: schemas.VendorBase
    
    class Config:
        orm_mode = True
    
    
class CreateProduct(ProductBase):
    '''Schema to create a new product'''
    
    pass


class UpdateProduct(ProductBase):
    '''Schema to update a product'''
    
    pass
