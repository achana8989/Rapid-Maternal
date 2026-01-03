from sqlalchemy import Column, Integer, String, DateTime
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
    resolved_at = Column(DateTime, nullable=True)
