from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from .database import Base


class MaternalEmergency(Base):
    __tablename__ = "maternal_emergencies"

    id = Column(Integer, primary_key=True)
    facility_id = Column(String, nullable=False)
    emergency_type = Column(String, nullable=False)
    status = Column(String, default="active")
    note = Column(String(200))

    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String)
    resolved_at = Column(DateTime)
    escalation_level = Column(Integer, default=0)
    escalated_at = Column(DateTime)


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True)
    emergency_id = Column(Integer, ForeignKey("maternal_emergencies.id"))
    escalation_level = Column(Integer)
    channel = Column(String)
    recipient = Column(String)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="sent")


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
