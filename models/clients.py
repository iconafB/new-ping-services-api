from sqlalchemy import String,Integer,Boolean,DateTime,ForeignKey,func
from sqlalchemy.orm import Mapped,mapped_column,DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Clients(Base):
    __tablename__="clients"
    client_id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    client_name:Mapped[str]=mapped_column(String(255),nullable=False)
    #branch:Mapped[int]=mapped_column(Integer,nullable=True)
    created_by:Mapped[int]=mapped_column(Integer,ForeignKey("users.id"),nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())