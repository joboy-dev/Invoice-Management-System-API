from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.user import models as user_models, schemas as user_schemas, oauth2
from app.database import get_db
from . import permissions

admin_payment_router = APIRouter(prefix='/admin/payment', tags=['Admin [Payment]'])