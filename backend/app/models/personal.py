from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class PersonalSubject(Base):
    __tablename__ = "personal_subjects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True)
    target_percentage = Column(Float, default=75.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_personal_subject"),
    )

    # Relationships
    user = relationship("User", back_populates="personal_subjects")
    records = relationship("PersonalRecord", back_populates="subject", cascade="all, delete-orphan")


class PersonalRecord(Base):
    __tablename__ = "personal_records"

    id = Column(Integer, primary_key=True, index=True)
    personal_subject_id = Column(Integer, ForeignKey("personal_subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    record_date = Column(Date, nullable=False, index=True)
    status = Column(String(50), nullable=False)  # PRESENT, ABSENT, HALF_DAY, CANCELLED
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("personal_subject_id", "record_date", name="uq_personal_subject_date"),
    )

    # Relationships
    subject = relationship("PersonalSubject", back_populates="records")
