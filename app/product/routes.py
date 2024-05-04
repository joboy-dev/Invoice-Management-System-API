import uuid
from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.user import oauth2, permissions as user_permissions, models as user_models

from . import models
from . import schemas
from . import permissions as product_permissions

product_router = APIRouter(prefix='/products', tags=['Products'])

@product_router.get('', status_code=status.HTTP_200_OK, response_model=List[schemas.ProductResponse])
def get_all_products(name: str = '', limit: int = 10, skip: int = 0, db: Session = Depends(get_db)):
    '''Endpoint to get all products and search for a product by name'''   
    
    # Search functionality
    products = db.query(models.Product).filter(models.Product.name.ilike(f'%{name}%')).limit(limit).offset(skip).all()
    
    return products


@product_router.post('/create', status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
def create_product(product_schema: schemas.CreateProduct, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to create a new product'''
    
    user_permissions.is_staff(current_user)
    
    # get seller based on current logged in user
    seller = db.query(user_models.Seller).filter(user_models.Seller.user_id == current_user.id).first()
    
    new_product = models.Product(
        **product_schema.model_dump(),
        seller_id=seller.id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@product_router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.ProductResponse)
def get_product_by_id(id, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get a specific product'''
    
    product = db.get(models.Product, ident=id)
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This product does not exist')
    
    return product


@product_router.patch('/{id}/update', status_code=status.HTTP_200_OK, response_model=schemas.ProductResponse)
def update_product(id, product_schema: schemas.UpdateProduct, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to update a specific product'''   
    
    user_permissions.is_staff(current_user)
    
    product_query = db.query(models.Product).filter(models.Product.id == id)
    
    product = product_query.first()
    seller = db.query(user_models.Seller).filter(user_models.Seller.user_id == current_user.id).first()
    
    product_permissions.is_product_owner(seller, product)
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This product does not exist')
    
    product_query.update(product_schema.model_dump(), synchronize_session=False) 
    db.commit()
    
    return product_query.first()


@product_router.delete('/{id}/delete', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to delete a specific product''' 
    
    user_permissions.is_staff(current_user)
    
    product = db.get(models.Product, ident=id)
    seller = db.query(user_models.Seller).filter(user_models.Seller.user_id == current_user.id).first()
    
    product_permissions.is_product_owner(seller, product)
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This product does not exist')
    
    db.delete(product)
    db.commit()
    
    return {'message': f'Product {product.name} deleted'}
