from sqlalchemy import String,Boolean,func,DateTime
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from datetime import datetime
class Base(DeclarativeBase):
    __table__="leads"
    

class Leads(Base):
    lead_name:Mapped[str]=mapped_column(String(255),nullable=True)
    last_aid:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    first_nme:Mapped[str]=mapped_column(String(255),nullable=True)
    id_number:Mapped[str]=mapped_column(String(13),nullable=True)
    cell_number:Mapped[str]=mapped_column(String(10),nullable=False)
    is_active:Mapped[bool]=mapped_column(Boolean,default=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())