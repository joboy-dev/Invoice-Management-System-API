from typing import List
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.user import models as user_models, oauth2
from app.product import schemas as product_schemas, models as product_models

from . import permissions, schemas

admin_product_router = APIRouter(prefix='/admin/products', tags=['Admin [Product]'])

@admin_product_router.get('', status_code=status.HTTP_200_OK, response_model=List[product_schemas.ProductResponse])
def get_vendor_products(name: str = '', limit: int = 20, skip: int = 0, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get all products for a vendor and search for a product by name'''
    
    permissions.is_admin(current_user)
    
    # Search functionality
    products = db.query(product_models.Product).filter(
        product_models.Product.name.ilike(f'%{name}%')
    ).limit(limit).offset(skip).all()
    
    return products


@admin_product_router.post('/create', status_code=status.HTTP_201_CREATED, response_model=product_schemas.ProductResponse)
def create_product(product_schema: product_schemas.CreateProduct, vendor_id: uuid.UUID | None,  db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to create a new product'''
    
    permissions.is_admin(current_user)
    
    new_product = product_models.Product(
        **product_schema.model_dump(),
        vendor_id=vendor_id if vendor_id is not None else None
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@admin_product_router.get('/{id}/fetch', status_code=status.HTTP_200_OK, response_model=product_schemas.ProductResponse)
def get_product_by_id(id, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get a specific product'''
    
    product = db.get(product_models.Product, ident=id)
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This product does not exist')
        
    return product


@admin_product_router.put('/{id}/update', status_code=status.HTTP_200_OK, response_model=product_schemas.ProductResponse)
def update_product(id, schema: schemas.AdminProductBase, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to update a specific product'''   
    
    permissions.is_admin(current_user)
    
    product_query = db.query(product_models.Product).filter(product_models.Product.id == id)
    product = product_query.first()
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This product does not exist')
        
    product_query.update(schema.model_dump(), synchronize_session=False) 
    db.commit()
    
    return product_query.first()


@admin_product_router.delete('/{id}/delete', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to delete a specific product''' 
    
    permissions.is_admin(current_user)
    
    product = db.get(product_models.Product, ident=id)
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This product does not exist')
    
    db.delete(product)
    db.commit()
    