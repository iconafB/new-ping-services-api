from sqlalchemy import String,Integer,func,Boolean,DateTime
from sqlalchemy.orm import Mapped,mapped_column,DeclarativeBase
from typing import List,Optional
from datetime import datetime
from config.database import Base

class Admin(Base):
    __tablename__="admin"
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    email:Mapped[str]=mapped_column(String(255),nullable=False,index=True)
    password:Mapped[str]=mapped_column(String(255),nullable=False)
    first_name:Mapped[str]=mapped_column(String(255),nullable=False)
    last_name:Mapped[str]=mapped_column(String(255),nullable=False)
    is_admin:Mapped[bool]=mapped_column(Boolean,nullable=False,default=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now())
