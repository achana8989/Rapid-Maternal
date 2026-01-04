from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from .database import Base


class MaternalEmergency(Base):
    __tablename__ = "maternal_emergencies"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(String, nullable=False)
    emergency_type = Column(String, nullable=False)
    status = Column(String, default="active")
    note = Column(String(200), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    escalation_level = Column(Integer, default=0)
    escalated_at = Column(DateTime, nullable=True)
    
class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True)
    emergency_id = Column(Integer, ForeignKey("maternal_emergencies.id"), nullable=False)
    escalation_level = Column(Integer, nullable=False)
    channel = Column(String, nullable=False)  # SMS, WhatsApp, Email
    recipient = Column(String, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="sent")
