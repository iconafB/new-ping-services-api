from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import Integer,String,DateTime,ForeignKey,func,Boolean
from datetime import datetime
from config.database import Base
#client tokens are meant to be used by the clients to fetch their pings payloads

class client_tokens(Base):
    __tablename__="clients_tokens"
    pk:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True,nullable=False)
    unique_token:Mapped[str]=mapped_column(String,nullable=False)
    created_by:Mapped[int]=mapped_column(Integer,ForeignKey("clients_table.client_id"))
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now())
    is_active:Mapped[bool]=mapped_column(Boolean,nullable=False)

