from uuid import uuid4
from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

from app.database import Base

class Invoice(Base):
    '''Invoice model'''
    
    __tablename__ = 'invoices'
    
    id = sa.Column(sa.UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
