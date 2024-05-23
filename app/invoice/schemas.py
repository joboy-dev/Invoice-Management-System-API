from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel
from typing import List

from app.user import schemas as user_schemas
from app.product import schemas as product_schemas
from app.invoice.models import Status

class InvoiceItemBase(BaseModel):
    '''Invoice item base schema'''
    
    description: str
    quantity: int = 1
    tax: float | None = 0.0
    discount: float | None = 0.0
    additional_charges: float | None = 0.0
    

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
    product: product_schemas.ProductResponse
    
    class Config:
        orm_mode=True
        

class UpdateInvoiceItem(BaseModel):
    '''Invoice item update schema'''
    
    description: str
    quantity: int = 1
    tax: float | None = 0.0
    discount: float | None = 0.0
    additional_charges: float | None = 0.0
    

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
    invoice_items: List[InvoiceItemResponse]
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
    