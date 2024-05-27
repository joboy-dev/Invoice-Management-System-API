from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.user import models as user_models, oauth2
from app.payment import schemas as payment_schemas, models as payment_models
from app.database import get_db
from . import permissions

admin_payment_router = APIRouter(prefix='/admin/payment', tags=['Admin [Payment]'])

@admin_payment_router.get('/all', status_code=status.HTTP_200_OK, response_class=List[payment_schemas.PaymentResponse])
def get_all_payments(db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get all payments'''
    
    permissions.is_admin(current_user)
    
    payments = db.query(payment_models.Payment).all()
    
    return payments


@admin_payment_router.get('/{id}/fetch', status_code=status.HTTP_200_OK, response_class=payment_schemas.PaymentResponse)
def get_payment_by_id(id: UUID, db: Session = Depends(get_db), current_user: user_models.User = Depends(oauth2.get_current_user)):
    '''Endpoint to get a single payment record'''
    
    permissions.is_admin(current_user)
    
    payment = db.query(payment_models.Payment).filter(payment_models.Payment.id == id).first()
    
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Payment record not found')
    
    return payment
    