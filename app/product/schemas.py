from pydantic import BaseModel

class ProductSchema(BaseModel):
    '''Product pydantic schema'''
    
    name: str
    description: str
    unit_price: float = 0.00