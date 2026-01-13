# app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy
import os

# SQLite URL (or change to your DB)
SQLALCHEMY_DATABASE_URL = "sqlite:///./rapid_maternal.db"

# Engine and SessionLocal
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create tables if missing and apply simple migrations for SQLite.
    Adds `full_name`, `email`, and `facility_id` columns to `users` if absent.
    """
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # For SQLite, attempt simple ALTER TABLE to add missing columns
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
        try:
            with engine.connect() as conn:
                res = conn.execute(sqlalchemy.text("PRAGMA table_info('users')"))
                existing = {row[1] for row in res.fetchall()} if res is not None else set()

                migrations = []
                if 'full_name' not in existing:
                    migrations.append("ALTER TABLE users ADD COLUMN full_name VARCHAR")
                if 'email' not in existing:
                    migrations.append("ALTER TABLE users ADD COLUMN email VARCHAR")
                if 'facility_id' not in existing:
                    migrations.append("ALTER TABLE users ADD COLUMN facility_id INTEGER")

                for sql in migrations:
                    try:
                        conn.execute(sqlalchemy.text(sql))
                    except Exception:
                        # best-effort: ignore failures
                        pass
                # Add columns to maternal_emergencies if missing
                res2 = conn.execute(sqlalchemy.text("PRAGMA table_info('maternal_emergencies')"))
                existing2 = {row[1] for row in res2.fetchall()} if res2 is not None else set()
                me_migrations = []
                if 'acknowledged_by' not in existing2:
                    me_migrations.append("ALTER TABLE maternal_emergencies ADD COLUMN acknowledged_by VARCHAR")
                if 'acknowledged_at' not in existing2:
                    me_migrations.append("ALTER TABLE maternal_emergencies ADD COLUMN acknowledged_at DATETIME")

                for sql in me_migrations:
                    try:
                        conn.execute(sqlalchemy.text(sql))
                    except Exception:
                        pass
        except Exception:
            pass
