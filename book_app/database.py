import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


db_url = os.getenv('SQLALCHEMY_DATABASE_URL', 'postgres://admin:password@localhost:5432/resola')
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
