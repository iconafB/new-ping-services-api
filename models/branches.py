from sqlalchemy import String,Boolean,Integer,func,DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from config.database import Base

class Branches(Base):
    
    __tablename__="branches"
    branch_id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    branch_name:Mapped[str]=mapped_column(String(255),nullable=False)
    created_by:Mapped[int]=mapped_column(Integer,ForeignKey("admin.id"),nullable=False)
    is_active:Mapped[bool]=mapped_column(Boolean,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())