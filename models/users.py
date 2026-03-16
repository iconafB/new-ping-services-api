from sqlalchemy import String,Boolean,Integer,DateTime,func
from sqlalchemy.orm import Mapped,mapped_column,DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__="users"
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    first_name:Mapped[str]=mapped_column(String(255),nullable=False)
    last_name:Mapped[str]=mapped_column(String(255),nullable=False)
    password:Mapped[str]=mapped_column(String(255),nullable=False)
    email:Mapped[str]=mapped_column(String(255),nullable=False,unique=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now())

