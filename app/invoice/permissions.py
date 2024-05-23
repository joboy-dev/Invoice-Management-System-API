from fastapi import HTTPException, status

from app.user.models import Vendor, Customer
from .models import Invoice

def is_invoice_vendor(vendor: Vendor, invoice: Invoice):
    '''Permission to check if the current logged in seller user is the owner of an invoice'''
    
    if invoice.vendor_id != vendor.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=' You do not have access to make changes to this invoice')


def is_invoice_customer(customer: Customer, invoice: Invoice):
    '''Permission to check if the current logged in customer user is the owner of an invoice'''
    
    if invoice.vendor_id != customer.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=' You do not have access to make changes to this invoice')
    