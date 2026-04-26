from fastapi import Depends
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from db.config import settings
from typing import Annotated

engine = create_engine(
    settings.DB_URL, 
    pool_size=10, 
    max_overflow=20, 
    pool_timeout=30, 
    pool_recycle=3600, 
    pool_pre_ping=True
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



