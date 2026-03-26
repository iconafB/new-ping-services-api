from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import Integer,String,DateTime,ForeignKey,func,Boolean
from datetime import datetime
from config.database import Base
#client tokens are meant to be used by the clients to fetch their pings payloads
# we will use opaque api keys no, this is the wrong approach

class pings_retrieval_tokens(Base):
    __tablename__="pings_retrieval_tokens"
    pk:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True,nullable=False)
    token_hash:Mapped[str]=mapped_column(String,nullable=False,unique=True,index=True)
    client_id:Mapped[int]=mapped_column(Integer,ForeignKey("clients_table.client_id"),nullable=False,index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now())
    is_used:Mapped[bool]=mapped_column(Boolean,nullable=False,default=False)
    used_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=True)
    is_active:Mapped[bool]=mapped_column(Boolean,nullable=False,default=False)

