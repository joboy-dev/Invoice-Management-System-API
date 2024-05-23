from uuid import UUID
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.user import models as user_models, oauth2, permissions as user_permissions
from app.invoice import permissions as invoice_permissions, models as invoice_models

from .models import Payment
from . import schemas

payment_router = APIRouter(prefix='/payment', tags=['Payments'])

@payment_router.post('/{invoice_id}/pay', status_code=status.HTTP_200_OK)
def process_payment_for_invoice(invoice_id: UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to process payment for an invoice'''
    
    user_permissions.default_permission(current_user)
    
    customer = db.query(user_models.Customer).filter(user_models.Customer.user_id == current_user.id).first()
    invoice = db.get(invoice_models.Invoice, ident=invoice_id)
    
    invoice_permissions.is_invoice_customer(customer, invoice)
    
    if invoice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invoice not found')
    
    # TODO: Process test payment with paystack. Ensure to catch exceptions
    
    # Update invoice payment status
    invoice.status = invoice_models.Status.paid
    
    # Add payment to payments table
    payment = Payment(
        amount_paid=invoice.total,
        invoice_id=invoice.id,
        customer_id=invoice.customer_id,
        vendor_id=invoice.vendor_id
    )
    db.add(payment)
    
    db.commit()
    
    return {'message': 'Invoice payment completed successfully'}


@payment_router.get('/customer/all', status_code=status.HTTP_200_OK, response_class=List[schemas.PaymentResponse])
def get_all_payments_for_customer(db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get all payment for a customer'''
    
    user_permissions.is_customer(current_user)
    
    customer = db.query(user_models.Customer).filter(user_models.Customer.user_id == current_user.id).first()
    
    payments = db.query(Payment).filter(Payment.customer_id == customer.id).all()
    
    return payments


@payment_router.get('/vendor/all', status_code=status.HTTP_200_OK, response_class=List[schemas.PaymentResponse])
def get_all_payments_for_vendor(db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get all payment for a customer'''
    
    user_permissions.is_vendor(current_user)
    
    vendor = db.query(user_models.Vendor).filter(user_models.Vendor.user_id == current_user.id).first()
    
    payments = db.query(Payment).filter(Payment.vendor_id == vendor.id).all()
    
    return payments


@payment_router.get('/{id}/fetch', status_code=status.HTTP_200_OK, response_class=schemas.PaymentResponse)
def get_payment_by_id(id: UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get a single payment record'''
    
    user_permissions.default_permission(current_user)
    
    payment = db.query(Payment).filter(Payment.id == id).first()
    
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Payment record not found')
    
    return payment
    