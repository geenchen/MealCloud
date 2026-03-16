from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

from config import settings

engine = create_engine(
    settings.DATABASE_URL.replace('+aiosqlite', ''),
    connect_args={'check_same_thread': False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_tables():
    from models.user import User  # noqa: F401
    from models.dish import Dish, Category  # noqa: F401
    from models.order import Order, OrderItem, Table  # noqa: F401
    from models.area import Area  # noqa: F401
    from models.reservation import Reservation  # noqa: F401

    Base.metadata.create_all(bind=engine)


database = Database(settings.DATABASE_URL)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()