from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///data/pharma_radar.db"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine)


def get_session():
    return SessionLocal()


def init_db():
    from database.models import Base

    Base.metadata.create_all(bind=engine)
