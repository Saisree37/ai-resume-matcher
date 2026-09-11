from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)
session = sessionmaker(autoflush=False,autocommit=False,bind=engine)

Base = declarative_base()