# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# For now, we use SQLite (a simple file database) so you don't need to install anything complex.
# Later, we can switch this one line to connect to PostgreSQL for the real app.
SQLALCHEMY_DATABASE_URL = "sqlite:///./restaurant_app.db"

# Create the engine (the connection)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session factory (to talk to the database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The base class for our models
Base = declarative_base()