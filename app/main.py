from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .user.views import user_router
from .product.views import product_router

# Models
from .user import models as user_models
from .product import models as product_models

from app.database import engine

# Create all models
user_models.Base.metadata.create_all(bind=engine)
product_models.Base.metadata.create_all(bind=engine)

# --------------------------------------------------------
# App configurations
# --------------------------------------------------------

app = FastAPI(
    title='Invoice Management System',
    version='1.0',
    description='A system used to manage invoices of products purchased. Can be especially useful for retail stores and even big supermarkets.',
)

# Allowed hosts
origins = ['https://localhost:3000']

# Add CORS midddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# Include routes
app.include_router(user_router)
app.include_router(product_router)
