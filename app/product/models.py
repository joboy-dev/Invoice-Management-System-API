from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

from app.database import Base

class Product(Base):
    '''Products model'''
    
    __tablename__ = 'products'
    
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    name = sa.Column(sa.String(length=255), nullable=False, index=True)
    description = sa.Column(sa.String(length=255), nullable=False)
    unit_price = sa.Column(sa.Float, nullable=False, server_default='0.00')
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    vendor_id = sa.Column(sa.UUID(as_uuid=True), sa.ForeignKey('vendors.id', ondelete='CASCADE'))
    vendor = relationship('Vendor', back_populates='products')
    invoice_item = relationship('InvoiceItem', back_populates='product')
    