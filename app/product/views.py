from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.user.permissions import UserPermissions

from .models import Product
from .schemas import ProductSchema

product_router = APIRouter(prefix='/products')

@product_router.get('', status_code=status.HTTP_200_OK)
def get_all_products(limit: int = 10, skip: int = 2, db: Session = Depends(get_db)):
    '''Endpoint to get all products'''
    
    products = db.query(Product).all()
    return products


@product_router.post('/create', status_code=status.HTTP_201_CREATED, response_model=ProductSchema)
def create_product(product: ProductSchema, db: Session = Depends(get_db)):
    '''Endpoint to creata a new product'''
    
    new_product = Product(
        **product.model_dump()
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@product_router.get('/search', status_code=status.HTTP_200_OK)
def search_products_by_name(q: str, db: Session = Depends(get_db)):
    '''Endpoint to search for a product by name'''   
    
    # Search functionality
    products = db.query(Product).filter(Product.name.ilike(f'%{q}%')).all()
    
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No products found')
    
    return products


@product_router.get('/{id}', status_code=status.HTTP_200_OK)
def get_product_by_id(id, db: Session = Depends(get_db)):
    '''Endpoint to get a specific product'''   
    
    product = db.get(Product, ident=id)
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This product does not exist')
    
    return product


@product_router.patch('/{id}/update', status_code=status.HTTP_200_OK)
def update_product(id, product_model: ProductSchema, db: Session = Depends(get_db)):
    '''Endpoint to update a specific product'''   
    
    product_query = db.query(Product).filter(Product.id == id)
    product = product_query.first()
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This product does not exist')
    
    product_query.update(product_model.model_dump(), synchronize_session=False) 
    db.commit()
    
    return product_query.first()


@product_router.delete('/{id}/delete', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id, db: Session = Depends(get_db)):
    '''Endpoint to delete a specific product'''   
    
    product = db.get(Product, ident=id)
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='This product does not exist')
    
    db.delete(product)
    db.commit()
    
    return {'message': f'Product {product.name} deleted'}