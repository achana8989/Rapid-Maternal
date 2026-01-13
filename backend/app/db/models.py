# backend/app/db/models.py
from sqlalchemy import Column, Integer, String, DateTime
from app.db.database import Base
from datetime import datetime
from passlib.hash import bcrypt

class MaternalEmergency(Base):
    __tablename__ = "maternal_emergencies"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, nullable=False)
    emergency_type = Column(String, nullable=False)
    status = Column(String, default="pending")
    note = Column(String, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    escalation_level = Column(String, default="low")
    created_at = Column(DateTime, default=datetime.utcnow)


class Facility(Base):
    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    emergency_id = Column(Integer, nullable=False)
    level = Column(String, nullable=False)
    message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ✅ Add this User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # e.g., MIDWIFE, CHPS, ADMIN
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    facility_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
