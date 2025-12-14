from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    due_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    frequency = Column(String, nullable=False)  # monthly, quarterly, annual
    category = Column(String, default="business")  # business / personal
    gst_credit = Column(Boolean, default=True)
    notes = Column(String, default="")
    active = Column(Boolean, default=True)
