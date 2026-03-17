from sqlalchemy import String,Boolean,Integer,DateTime,ForeignKey,func
from sqlalchemy.orm import Mapped,mapped_column,DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Credits(Base):
    __tablename__='credits_table'
    credits_id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    credits_total:Mapped[int]=mapped_column(Integer,nullable=True)
    created_by:Mapped[int]=mapped_column(Integer,ForeignKey("users.id"))

class Credits_History_Table(Base):
    __tablename__="credits_history_table"
    history_id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    credits_amount:Mapped[int]=mapped_column(Integer,nullable=False)
    created_by:Mapped[int]=mapped_column(Integer,ForeignKey("users.id"),nullable=False)
    is_active:Mapped[bool]=mapped_column(Boolean,nullable=False,default=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now())
