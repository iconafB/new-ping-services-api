from sqlalchemy import String,Boolean,Integer,Text,DateTime,func
from sqlalchemy.orm import Mapped,mapped_column,DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Clients_Table(Base):
    __tablename__="clients_table"
    client_id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    client_name:Mapped[str]=mapped_column(String(255),nullable=False,unique=True)
    email:Mapped[str]=mapped_column(String(255),nullable=False,unique=True,index=True)
    password:Mapped[str]=mapped_column(Text,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now())
    is_active:Mapped[bool]=mapped_column(Boolean,nullable=False,server_default="true")

