from uuid import uuid4
from enum import Enum
import random

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

from app.database import Base

def generate_invice_number():
    return random.randint(100000, 99999999999999)

class Status(str, Enum):
    '''Status enum for invoices'''
    
    draft='draft'
    pending='pending'
    paid='paid'
    overdue='overdue'

class Invoice(Base):
    '''Invoice model'''
    
    __tablename__ = 'invoices'
    
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    invoice_number = sa.Column(sa.BigInteger, unique=True, index=True, nullable=False, default=generate_invice_number)
    invoice_date = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    status = sa.Column(sa.Enum(Status), nullable=False, server_default=Status.draft.value)
    due_date = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False)
    total = sa.Column(sa.Numeric(10, 2), nullable=False, server_default='0.00')
    
    customer_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    customer = relationship('Customer', back_populates='invoices')
    
    vendor_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('vendors.id', ondelete='CASCADE'), nullable=False)
    vendor = relationship('Vendor', back_populates='invoices')
    
    invoice_items = relationship('InvoiceItem', back_populates='invoice')


class InvoiceItem(Base):
    '''Invoice item model'''
    
    __tablename__ = 'invoice_items'

    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    description = sa.Column(sa.String, nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False)
    unit_price = sa.Column(sa.Numeric(10, 2), nullable=False)
    tax = sa.Column(sa.Numeric(10, 2), nullable=False, server_default='0.00')
    discount = sa.Column(sa.Numeric(10, 2), nullable=False, server_default='0.00')
    additional_charges = sa.Column(sa.Numeric(10, 2), nullable=False, server_default='0.00')
    total_price = sa.Column(sa.Numeric(10, 2), nullable=False)

    invoice_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)
    invoice = relationship("Invoice", back_populates="invoice_items")
    
    product_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    product = relationship("Product", back_populates="invoice_item")
    