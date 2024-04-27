from fastapi import FastAPI, APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

invoice_router = APIRouter(prefix='/invoice', tags=['Invoice'])