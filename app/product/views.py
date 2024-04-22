from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from .models import Product, ProductModel

product_router = APIRouter()

@product_router.get('/products/all', status_code=status.HTTP_200_OK)
def get_all_products(db: Session = Depends(get_db)):
    '''Endpoint to get all products'''
    
    products = db.query(Product).all()
    return products


@product_router.post('/products/create', status_code=status.HTTP_201_CREATED, response_model=ProductModel)
def create_product(product: ProductModel, db: Session = Depends(get_db)):
    '''Endpoint to creata a new product'''
    
    new_product = Product(
        name=product.name, 
        description=product.description, 
        unit_price=product.unit_price
    )
    
    db.commit()
    
    return new_product
    
