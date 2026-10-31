from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Time, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class SessionStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    CONDUCTED = "CONDUCTED"
    CANCELLED = "CANCELLED"
    HOLIDAY = "HOLIDAY"


class HolidayType(str, enum.Enum):
    INSTITUTIONAL = "INSTITUTIONAL"
    WEEKLY = "WEEKLY"


class ClassSession(Base):
    __tablename__ = "class_sessions"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    topic = Column(String(255), nullable=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.SCHEDULED, nullable=False)
    is_attendance_submitted = Column(Boolean, default=False, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)  # Admin lock
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    classroom = relationship("ClassRoom", back_populates="sessions")
    subject = relationship("Subject", back_populates="sessions")
    teacher = relationship("User", back_populates="conducted_sessions")
    attendance_records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")
    audit_logs = relationship("AttendanceAuditLog", back_populates="session")


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    holiday_date = Column(Date, unique=True, index=True, nullable=False)
    holiday_type = Column(SQLEnum(HolidayType), default=HolidayType.INSTITUTIONAL, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
