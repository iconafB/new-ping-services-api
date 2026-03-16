from sqlalchemy import String,func,ForeignKey
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class PingsTable(Base):
    pings_id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    cell_number:Mapped[str]=mapped_column(String(10),nullable=False)
    pinged_date:Mapped[datetime]=mapped_column(server_default=func.now())
    pinged_status:Mapped[str]=mapped_column(String(255),nullable=False)