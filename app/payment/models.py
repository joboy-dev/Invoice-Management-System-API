from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

from app.database import Base

class Payment(Base):
    '''Payments table'''
    
    __tablename__ = 'payments'
    
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    amount_paid = sa.Column(sa.Numeric(10, 2), nullable=False, server_default='0.00')
    payment_date = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    invoice_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)
    invoice = relationship('Invoice', back_populates='payment')
    
    customer_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    customer = relationship('Customer', back_populates='payments')
    
    vendor_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('vendors.id', ondelete='CASCADE'), nullable=False)
    vendor = relationship('Vendor', back_populates='payments')
    
    