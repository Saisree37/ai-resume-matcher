from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer,DateTime, String
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer,primary_key=True)
    title = Column(String)
    company = Column(String)
    description = Column(String)
    created_at = Column(DateTime)

