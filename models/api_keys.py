from sqlalchemy import Boolean,String,Integer,DateTime,func
from sqlalchemy.orm import Mapped,mapped_column
from typing import Optional
from datetime import datetime
from config.database import Base


class ApiKey(Base):
    __tablename__="api_keys"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    name:Mapped[str]=mapped_column(String(120),nullable=False)
    owner_id:Mapped[Optional[int]]=mapped_column(Integer,nullable=False,index=True)
    key_prefix:Mapped[str]=mapped_column(String(32),nullable=False,unique=True,index=True)
    key_hash:Mapped[str]=mapped_column(String(64),nullable=False,unique=True,index=True)
    is_active:Mapped[bool]=mapped_column(Boolean,nullable=False,default=True)
    expires_at:Mapped[Optional[datetime]]=mapped_column(DateTime(timezone=True),nullable=True)
    last_used_at:Mapped[Optional[datetime]]=mapped_column(DateTime(timezone=True),nullable=True)
    revoved_at:Mapped[Optional[datetime]]=mapped_column(DateTime(timezone=True),nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now())