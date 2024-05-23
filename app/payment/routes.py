from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.user import models as user_models, oauth2
from app.invoice import permissions as invoice_permissions, models as invoice_models

from .models import Payment

payment_router = APIRouter(prefix='/payment', tags=['Payments'])

@payment_router.post('/{invoice_id}/pay', status_code=status.HTTP_200_OK)
def process_payment_for_invoice(invoice_id: UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to process payment for an invoice'''
    
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
        invoice_id=invoice.id
    )
    db.add(payment)
    
    db.commit()
    
    return {'message': 'Invoice payment completed successfully'}
    
    
    
    
    