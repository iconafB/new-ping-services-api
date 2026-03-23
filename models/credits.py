import enum
from sqlalchemy import Boolean,Integer,DateTime,ForeignKey,func,Enum
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from config.database import Base

class TransactionType(str,enum.Enum):
    Deposit="Deposit"
    Withdrawal="Withdrawal"
    Unknown="Unknown"

class Credits(Base):
    __tablename__='credits_table'
    credits_id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    credits_balance:Mapped[int]=mapped_column(Integer,nullable=True)
    is_active:Mapped[bool]=mapped_column(Boolean,nullable=False,default=True)
    created_by:Mapped[int]=mapped_column(Integer,ForeignKey("clients_table.client_id"),nullable=False)

class Credits_History_Table(Base):
    __tablename__="credits_history_table"
    history_id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    credits_amount:Mapped[int]=mapped_column(Integer,nullable=False,default=0)
    transaction_type:Mapped[TransactionType]=mapped_column(Enum(TransactionType,name="transaction_type", create_type=False),nullable=False,default=TransactionType.Unknown)
    created_by:Mapped[int]=mapped_column(Integer,ForeignKey("clients_table.client_id"),nullable=False)
    is_active:Mapped[bool]=mapped_column(Boolean,nullable=False,default=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False,server_default=func.now())
