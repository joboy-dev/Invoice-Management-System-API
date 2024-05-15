from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel
from typing import List

from app.user import schemas as user_schemas
from app.invoice.models import Status

class InvoiceItemBase(BaseModel):
    '''Invoice item base schema'''
    
    description: str
    quantity: int = 1
    unit_price: float
    tax: float | None = 0.0
    discount: float | None = 0.0
    additional_charges: float | None = 0.0
    
    @property
    def total_price_before_tax(self) -> float:
        return self.quantity * self.unit_price

    def total_price(self) -> float:
        total_before_tax = self.total_price_before_tax
        tax_amount = total_before_tax * (self.tax or 0.0)
        discount_amount = total_before_tax * (self.discount or 0.0)
        return total_before_tax + tax_amount - discount_amount + (self.additional_charges or 0.0)
    

class InvoiceItemResponse(BaseModel):
    '''Invoice item base schema'''
    
    id: uuid.UUID
    description: str
    quantity: int
    unit_price: float
    tax: float | None
    discount: float | None
    additional_charges: float | None
    total_price: float
    
    class Config:
        orm_mode=True
    

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ---------------------------------------------------------------------- 
    
    

class InvoiceBase(BaseModel):
    '''Invoice pydantic base model'''
    
    invoice_number: int
    invoice_date: datetime
    status: Status
    due_date: datetime
    

class InvoiceResponse(InvoiceBase):
    '''Invoice pydantic response model'''    
            
    id: uuid.UUID
    customer: user_schemas.CustomerResponse
    vendor: user_schemas.VendorBase
    items: List[InvoiceItemResponse]
    total: float
    
    class Config:
        orm_mode=True
    
    
class IssueInvoice(BaseModel):
    '''Issue invoice schema'''
    
    due_date: datetime = datetime.now() + timedelta(days=7)
    status: Status = Status.pending
    
    
class UpdateInvoiceStatus(BaseModel):
    '''Update invoice status schema'''
    
    status: Status = Status.pending
    