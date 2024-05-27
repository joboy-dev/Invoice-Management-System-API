import datetime as dt
from decimal import Decimal
from typing import List
import uuid

from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.product.models import Product
from app.user.oauth2 import get_current_user
from app.user.models import User, Customer, Vendor
from app.user import permissions as user_permissions
from . import models
from . import schemas
from . import permissions

invoice_router = APIRouter(prefix='/invoices', tags=['Invoice'])

def total_price(schema_obj, product_obj: Product):
    total_before_tax = schema_obj.quantity * product_obj.unit_price
    tax_amount = total_before_tax * (schema_obj.tax or 0.0)
    discount_amount = total_before_tax * (schema_obj.discount or 0.0)
    
    total_price = total_before_tax + tax_amount - discount_amount + (schema_obj.additional_charges or 0.0)
    return total_price


@invoice_router.get('', status_code=status.HTTP_200_OK, response_model=List[schemas.InvoiceResponse])
def get_vendor_invoices(filter: str = '', db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    '''Endpoint to get all invoices for current logged in vendor and filter them by draft, pending, paid, overdue'''
    
    user_permissions.is_vendor(current_user)
    
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    
    if filter == '':
        invoices = db.query(models.Invoice).filter(
            models.Invoice.vendor_id == vendor.id,
        ).all()
    else:
        invoices = db.query(models.Invoice).filter(
            models.Invoice.vendor_id == vendor.id,
            models.Invoice.status.in_([filter])
        ).all()
    
    return invoices


@invoice_router.get('/current-user/fetch', status_code=status.HTTP_200_OK, response_model=List[schemas.InvoiceResponse])
def get_current_user_invoices(filter: str = '', db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    '''Endpoint to get all invoices for current user and filter them by draft, pending, paid, overdue'''
    
    user_permissions.is_customer(current_user)
    
    customer = db.query(Customer).filter(Customer.user_id == current_user.id).first()
    
    if filter == '':
        invoices = db.query(models.Invoice).filter(
            models.Invoice.customer_id == customer.id,
            models.Invoice.status.in_(['pending', 'paid', 'overdue']),
        ).all()
    else:
        invoices = db.query(models.Invoice).filter(
            models.Invoice.customer_id == customer.id,
            models.Invoice.status.in_(['pending', 'paid', 'overdue']),
            models.Invoice.status.in_([filter])
        ).all()
    
    return invoices

    
@invoice_router.post('/issue/{customer_id}', status_code=status.HTTP_201_CREATED, response_model=schemas.InvoiceResponse)
def issue_invoice(customer_id: uuid.UUID, invoice_schema: schemas.IssueInvoice, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    '''Endpoint to create a new invoice'''
    
    user_permissions.is_vendor(current_user)
    
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    
    if invoice_schema.status not in ['draft', 'pending']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You can only save an invoice as draft or pending.')
    
    if dt.datetime.now().replace(tzinfo=None) >= invoice_schema.due_date.replace(tzinfo=None):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Due date cannot be in the past.')
    
    invoice = models.Invoice(
        **invoice_schema.model_dump(),
        customer_id=customer_id,
        vendor_id=vendor.id
    )
    
    db.add(invoice)
    db.commit()
    
    return invoice


@invoice_router.get('/{id}/fetch', status_code=status.HTTP_200_OK, response_model=schemas.InvoiceResponse)
def get_invoice_by_id(id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    '''Endpoint to get a simgle invoice by id'''
    
    user_permissions.default_permission(current_user)
    
    invoice = db.get(models.Invoice, ident=id)
    
    if invoice is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice not found.')
    
    return invoice


@invoice_router.put('/{id}/status/update', status_code=status.HTTP_200_OK, response_model=schemas.InvoiceResponse)
def update_invoice_status(id: uuid.UUID, schema: schemas.UpdateInvoiceStatus, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    '''Endpoint to get a simgle invoice by id'''
    
    user_permissions.is_vendor(current_user)
    
    invoice = db.get(models.Invoice, ident=id)
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    
    if invoice is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice not found.')
    
    permissions.is_invoice_vendor(vendor, invoice)
    
    if schema.status == 'draft':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invoice cannot be updated to a draft.')

    invoice.status = schema.status
    db.commit()
    
    return invoice


@invoice_router.post('/{invoice_id}/product/{product_id}/add', status_code=status.HTTP_200_OK, response_model=schemas.InvoiceItemResponse)
def add_item_to_invoice(invoice_id: uuid.UUID, product_id: uuid.UUID, schema: schemas.InvoiceItemBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    '''Endpoint to add an item(product) to an invoice'''
    
    user_permissions.is_vendor(current_user)
    
    vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    
    # Check if logged in user is the vender of the invoice or the product
    invoice_query = db.query(models.Invoice).filter(
        models.Invoice.id == invoice_id,
        models.Invoice.vendor_id == vendor.id
    )
    invoice = invoice_query.first()
    
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.vendor_id == vendor.id
    ).first()
    
    if invoice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice not found')
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')
    
    # Check if invoice item already exists for the invoice
    invoice_item = db.query(models.InvoiceItem).filter(
        models.InvoiceItem.invoice_id == invoice.id,
        models.InvoiceItem.product_id == product.id
    ).first()
    
    if invoice_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This product is already on this invoice')
    
    final_total = total_price(schema_obj=schema, product_obj=product)
    # Create new invoice item object
    item = models.InvoiceItem(
        **schema.model_dump(),
        unit_price=product.unit_price,
        total_price=final_total,
        invoice_id=invoice_id,
        product_id=product_id,
    )
    
    db.add(item)
    
    # Update the toal price of the invoice
    invoice.total += Decimal(final_total)
    
    db.commit()
    db.refresh(item)
    
    return item


# @invoice_router.delete('/{invoice_id}/product/{product_id}/remove', status_code=status.HTTP_204_NO_CONTENT)
# def remove_item_from_invoice(invoice_id: uuid.UUID, product_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     '''Endpoint to remove an item(product) from an invoice'''
    
#     user_permissions.is_vendor(current_user)
    
#     vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    
#     # Check if logged in user is the vender of the invoice or the product
#     invoice_query = db.query(models.Invoice).filter(
#         models.Invoice.id == invoice_id,
#         models.Invoice.vendor_id == vendor.id
#     )
#     invoice = invoice_query.first()
    
#     product = db.query(Product).filter(
#         Product.id == product_id,
#         Product.vendor_id == vendor.id
#     ).first()
    
#     if invoice is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice not found')
    
#     if product is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')
    
#     invoice_item_query = db.query(models.InvoiceItem).filter(
#         models.InvoiceItem.invoice_id == invoice_id,
#         models.InvoiceItem.product_id == product_id
#     )
    
#     # Check if invoice item doesn't exists for the invoice
#     invoice_item = invoice_item_query.first()
    
#     if not invoice_item:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This product does not exist on this invoice')
    
#     invoice_item_query.delete(synchronize_session=False)
    
#     # Update the toal price of the invoice
#     invoice.total -= invoice_item.total_price
    
#     db.commit()


@invoice_router.delete('/item/{invoice_item_id}/remove', status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_invoice(invoice_item_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    '''Endpoint to remove an item(product) from an invoice'''
    
    user_permissions.is_vendor(current_user)
    
    invoice_item = db.get(models.InvoiceItem, ident=invoice_item_id)
    
    if not invoice_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice item does not exist')
    
    product = db.get(Product, ident=invoice_item.product_id)
    invoice = db.get(models.Invoice, ident=invoice_item.invoice_id)
    
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product does not exist')
    
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice does not exist')
    
    db.delete(invoice_item)
    
    # Update the toal price of the invoice
    invoice.total -= invoice_item.total_price
    
    db.commit()
    

# @invoice_router.put('/{invoice_id}/product/{product_id}/update', status_code=status.HTTP_204_NO_CONTENT)
@invoice_router.put('/item/{invoice_item_id}/update', status_code=status.HTTP_200_OK, response_model=schemas.InvoiceItemResponse)
def update_item_in_invoice(invoice_item_id: uuid.UUID, schema: schemas.UpdateInvoiceItem, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    '''Endpoint to update an item(product) in an invoice'''
    
    user_permissions.is_vendor(current_user)
    
    # vendor = db.query(Vendor).filter(Vendor.user_id == current_user.id).first()
    
    # # Check if logged in user is the vender of the invoice or the product
    # invoice_query = db.query(models.Invoice).filter(
    #     models.Invoice.id == invoice_id,
    #     models.Invoice.vendor_id == vendor.id
    # )
    # invoice = invoice_query.first()
    
    # product = db.query(Product).filter(
    #     Product.id == product_id,
    #     Product.vendor_id == vendor.id
    # ).first()
    
    # if invoice is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice not found')
    
    # if product is None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product not found')
    
    # invoice_item_query = db.query(models.InvoiceItem).filter(
    #     models.InvoiceItem.invoice_id == invoice_id,
    #     models.InvoiceItem.product_id == product_id
    # )
    
    invoice_item_query = db.query(models.InvoiceItem).filter(models.InvoiceItem.id == invoice_item_id)
    invoice_item = invoice_item_query.first()
    
    if invoice_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Product invoice item not found')
    
    # Remove price of invoice item from invoice total before update
    invoice = db.get(models.Invoice, ident=invoice_item.invoice_id)
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
    