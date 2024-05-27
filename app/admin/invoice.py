import datetime as dt
from decimal import Decimal
import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.user import models as user_models, oauth2, permissions as user_permissions
from app.database import get_db
from app.product import models as product_models
from app.invoice import models as invoice_models, schemas as invoice_schemas

from . import permissions
from . import schemas

admin_invoice_router = APIRouter(prefix='/admin/invoices', tags=['Admin(Incoice)'])

def total_price(schema_obj, product_obj: product_models.Product):
    total_before_tax = schema_obj.quantity * product_obj.unit_price
    tax_amount = total_before_tax * (schema_obj.tax or 0.0)
    discount_amount = total_before_tax * (schema_obj.discount or 0.0)
    
    total_price = total_before_tax + tax_amount - discount_amount + (schema_obj.additional_charges or 0.0)
    return total_price


@admin_invoice_router.get('', status_code=status.HTTP_200_OK, response_model=List[invoice_schemas.InvoiceResponse])
def get_all_invoices(filter: str = '', db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get all invoices and filter them by draft, pending, paid, overdue'''
    
    permissions.is_admin(current_user)
    
    if filter == '':
        invoices = db.query(invoice_models.Invoice).all()
    else:
        invoices = db.query(invoice_models.Invoice).filter(invoice_models.Invoice.status.in_([filter])).all()
    
    return invoices

    
@admin_invoice_router.post('/issue', status_code=status.HTTP_201_CREATED, response_model=invoice_schemas.InvoiceResponse)
def issue_invoice(invoice_schema: schemas.AdminInvoiceBase, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint for admin to create a new invoice'''
    
    permissions.is_admin(current_user)
    
    if invoice_schema.status not in ['draft', 'pending', 'paid', 'overdue']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid invoice status option.')
    
    if dt.datetime.now().replace(tzinfo=None) >= invoice_schema.due_date.replace(tzinfo=None):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Due date cannot be in the past.')
    
    invoice = invoice_models.Invoice(
        **invoice_schema.model_dump()
    )
    
    db.add(invoice)
    db.commit()
    
    return invoice


@admin_invoice_router.get('/{id}/fetch', status_code=status.HTTP_200_OK, response_model=invoice_schemas.InvoiceResponse)
def get_invoice_by_id(id: uuid.UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get a simgle invoice by id'''
    
    user_permissions.default_permission(current_user)
    
    invoice = db.get(invoice_models.Invoice, ident=id)
    
    if invoice is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice not found.')
    
    return invoice


@admin_invoice_router.put('/{id}/update', status_code=status.HTTP_200_OK, response_model=invoice_schemas.InvoiceResponse)
def update_invoice(id: uuid.UUID, schema: schemas.AdminInvoiceBase, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get a simgle invoice by id'''
    
    permissions.is_admin(current_user)
    
    invoice_query = db.query(invoice_models.Invoice).filter(invoice_models.Invoice.id == id)
    invoice = invoice_query.first()
    
    if invoice is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice not found.')

    invoice_query.update(schema.model_dump(), synchronize_session=False)
    db.commit()
    
    return invoice


@admin_invoice_router.post('/{invoice_id}/product/{product_id}/add', status_code=status.HTTP_200_OK, response_model=invoice_schemas.InvoiceItemResponse)
def add_item_to_invoice(invoice_id: uuid.UUID, product_id: uuid.UUID, schema: schemas.AdminInvoiceItemBase, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to add an item(product) to an invoice'''
    
    permissions.is_admin(current_user)
    
    product = db.get(product_models.Product, ident=schema.product_id)
    invoice = db.get(invoice_models.Invoice, ident=schema.invoice_id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product does not exist')
    
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice does not exist')
    
    # Check if invoice item already exists for the invoice
    invoice_item = db.query(invoice_models.InvoiceItem).filter(
        invoice_models.InvoiceItem.invoice_id == schema.invoice_id,
        invoice_models.InvoiceItem.product_id == schema.product_id
    ).first()
    
    if invoice_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This product is already on this invoice')
    
    final_total = total_price(schema_obj=schema, product_obj=product)
    
    # Create new invoice item object
    item = invoice_models.InvoiceItem(
        **schema.model_dump()
    )
    
    db.add(item)
    
    # Update the toal price of the invoice
    invoice.total += Decimal(final_total)
    
    db.commit()
    db.refresh(item)
    
    return item


@admin_invoice_router.delete('/item/{invoice_item_id}/remove', status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_invoice(invoice_item_id: uuid.UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to remove an item(product) from an invoice'''
    
    permissions.is_admin(current_user)
    
    invoice_item = db.get(invoice_models.InvoiceItem, ident=invoice_item_id)
    
    if not invoice_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice item does not exist')
    
    product = db.get(product_models.Product, ident=invoice_item.product_id)
    invoice = db.get(invoice_models.Invoice, ident=invoice_item.invoice_id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product does not exist')
    
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice does not exist')
    
    db.delete(invoice_item)
    
    # Update the toal price of the invoice
    invoice.total -= invoice_item.total_price
    
    db.commit()
    

# @admin_invoice_router.put('/{invoice_id}/product/{product_id}/update', status_code=status.HTTP_204_NO_CONTENT)
@admin_invoice_router.put('/item/{invoice_item_id}/update', status_code=status.HTTP_200_OK, response_model=invoice_schemas.InvoiceItemResponse)
def update_item_in_invoice(invoice_item_id: uuid.UUID, schema: schemas.AdminInvoiceItemBase, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to update an item(product) in an invoice'''
    
    permissions.is_admin(current_user)
    
    invoice_item_query = db.query(invoice_models.InvoiceItem).filter(invoice_models.InvoiceItem.id == invoice_item_id)
    invoice_item = invoice_item_query.first()
    
    if invoice_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product invoice item not found')
    
    # Remove price of invoice item from invoice total before update
    invoice = db.get(invoice_models.Invoice, ident=invoice_item.invoice_id)
    invoice.total -= invoice_item.total_price
    db.commit()
    
    invoice_item_query.update(schema.model_dump(), synchronize_session=False)
    
    final_total = total_price(schema_obj=schema, product_obj=invoice_item.product)
    # Update the invoice item total price
    invoice_item.total_price = final_total
    # Add the updated price back to invoice total
    invoice.total += Decimal(final_total)
    
    db.commit()
    
    return invoice_item
    