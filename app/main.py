from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .user.routes import user_router
from .user.auth import auth_router
from .product.routes import product_router
from .invoice.routes import invoice_router
from .payment.routes import payment_router

from .admin.user import admin_user_router
from .admin.product import admin_product_router
from .admin.invoice import admin_invoice_router
from .admin.payment import admin_payment_router

# --------------------------------------------------------------
# App configurations
# --------------------------------------------------------------

app = FastAPI(
    title='Invoice Management System',
    version='1.0',
    description='''
        A system used to manage invoices of products purchased. Can be especially useful for retail stores and even big supermarkets.
        The kind of token that will be used in this API is bearer token.\n
        For testing purposes, during the authorization in this documentation, you need your username and password.\n
        If you then want to use the API, use this header instead:
            'Authorization': 'Bearer token'
            Token will be gotten from the login endpoint.
    '''
)

# Allowed hosts
origins = ['*']

# Add CORS midddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# Include routes
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(invoice_router)
app.include_router(payment_router)

app.include_router(admin_user_router)
app.include_router(admin_product_router)
app.include_router(admin_invoice_router)
app.include_router(admin_payment_router)
