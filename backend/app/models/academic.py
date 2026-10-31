from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class ClassRoom(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # e.g., "B.Tech CSE"
    section = Column(String(50), nullable=False)  # e.g., "Section A"
    academic_year = Column(String(50), nullable=False)  # e.g., "2025-2026"
    description = Column(String(255), nullable=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "section", "academic_year", name="uq_class_section_year"),
    )

    # Relationships
    students = relationship("Student", back_populates="classroom", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="classroom", cascade="all, delete-orphan")
    teacher_assignments = relationship("TeacherAssignment", back_populates="classroom", cascade="all, delete-orphan")
    sessions = relationship("ClassSession", back_populates="classroom")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    roll_number = Column(String(50), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    student_identifier = Column(String(100), unique=True, index=True, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("roll_number", "class_id", name="uq_student_roll_class"),
    )

    # Relationships
    classroom = relationship("ClassRoom", back_populates="students")
    user = relationship("User", back_populates="student_profile")
    attendance_records = relationship("AttendanceRecord", back_populates="student", cascade="all, delete-orphan")
    audit_logs = relationship("AttendanceAuditLog", back_populates="student")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # e.g., "Data Structures"
    code = Column(String(50), nullable=False, index=True)  # e.g., "CS201"
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("code", "class_id", name="uq_subject_code_class"),
    )

    # Relationships
    classroom = relationship("ClassRoom", back_populates="subjects")
    teacher_assignments = relationship("TeacherAssignment", back_populates="subject", cascade="all, delete-orphan")
    sessions = relationship("ClassSession", back_populates="subject")


class TeacherAssignment(Base):
    __tablename__ = "teacher_assignments"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("teacher_id", "subject_id", "class_id", name="uq_teacher_subject_class"),
    )

    # Relationships
    teacher = relationship("User", back_populates="teacher_assignments")
    subject = relationship("Subject", back_populates="teacher_assignments")
    classroom = relationship("ClassRoom", back_populates="teacher_assignments")
