from fastapi import HTTPException, status

from app.user.models import Seller
from .models import Product

def is_product_owner(seller: Seller, product: Product):
    '''Permission to check if the current logged in seller user is the owner of a product'''
    
    if product.seller_id != seller.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=' You do not have access to make changes to this product')
    