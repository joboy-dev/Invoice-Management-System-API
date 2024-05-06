from fastapi import HTTPException, status

from app.user.models import Vendor
from .models import Product

def is_product_vendor(vendor: Vendor, product: Product):
    '''Permission to check if the current logged in seller user is the owner of a product'''
    
    if product.vendor_id != vendor.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=' You do not have access to make changes to this product')
    