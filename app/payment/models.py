from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

from app.database import Base

class Payment(Base):
    '''Payments table'''
    
    __tablename__ = 'payments'
    
    
    