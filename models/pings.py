from sqlalchemy import String,func,ForeignKey,Integer,text,Date,Text
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime,date
from config.database import Base


class PingsInput(Base):
    __tablename__="pings_input"
    ping_pk:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    cell_number:Mapped[str]=mapped_column(String(10),nullable=False,unique=True)
    pinged_status:Mapped[str]=mapped_column(String(255),nullable=False)
    creaed_date:Mapped[datetime]=mapped_column(server_default=func.now())
    pinged_by:Mapped[int]=mapped_column(Integer,ForeignKey("clients_table.client_id"))

class pinged_input(Base):
    __tablename__="pinged_input"
    cell_number:Mapped[str]=mapped_column(Text,primary_key=True)
    extract_date:Mapped[str]=mapped_column(Text)


class PingsOutputStatus(Base):
    __tablename__="pings_output_status"
    pk:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    cell_number:Mapped[str]=mapped_column(String(10),nullable=False)
    status:Mapped[str]=mapped_column(String,nullable=True)
    duration:Mapped[str]=mapped_column(String(10),nullable=True)
    ping_load_date:Mapped[date]=mapped_column(Date,nullable=False,server_default=text('CURRENT_DATE'))
    pinged_date:Mapped[date]=mapped_column(Date,nullable=False,server_default=text('CURRENT_DATE'))
    model_output:Mapped[str]=mapped_column(String,nullable=False)
    cli:Mapped[str]=mapped_column(String(11),nullable=False)