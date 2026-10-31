from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.TEACHER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    teacher_assignments = relationship("TeacherAssignment", back_populates="teacher", cascade="all, delete-orphan")
    conducted_sessions = relationship("ClassSession", back_populates="teacher")
    audit_logs = relationship("AttendanceAuditLog", back_populates="changed_by")
    student_profile = relationship("Student", back_populates="user", uselist=False)
    personal_subjects = relationship("PersonalSubject", back_populates="user", cascade="all, delete-orphan")
