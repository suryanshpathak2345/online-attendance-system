from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Classroom Schemas
class ClassRoomBase(BaseModel):
    name: str
    section: str
    academic_year: str
    description: Optional[str] = None


class ClassRoomCreate(ClassRoomBase):
    pass


class ClassRoomUpdate(BaseModel):
    name: Optional[str] = None
    section: Optional[str] = None
    academic_year: Optional[str] = None
    description: Optional[str] = None
    is_archived: Optional[bool] = None


class ClassRoomResponse(ClassRoomBase):
    id: int
    is_archived: bool
    created_at: datetime
    student_count: Optional[int] = 0
    subject_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Subject Schemas
class SubjectBase(BaseModel):
    name: str
    code: str
    class_id: int


class SubjectCreate(SubjectBase):
    teacher_id: Optional[int] = None  # Optionally assign teacher directly upon creation


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None


class SubjectResponse(SubjectBase):
    id: int
    created_at: datetime
    class_name: Optional[str] = None
    class_section: Optional[str] = None
    assigned_teacher_id: Optional[int] = None
    assigned_teacher_name: Optional[str] = None

    class Config:
        from_attributes = True


# Student Schemas
class StudentBase(BaseModel):
    full_name: str
    roll_number: str
    email: Optional[str] = None
    student_identifier: str
    class_id: int
    is_active: bool = True


class StudentCreate(StudentBase):
    password: Optional[str] = None  # If student login account should be created


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    roll_number: Optional[str] = None
    email: Optional[str] = None
    student_identifier: Optional[str] = None
    class_id: Optional[int] = None
    is_active: Optional[bool] = None


class StudentResponse(StudentBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    class_name: Optional[str] = None
    class_section: Optional[str] = None

    class Config:
        from_attributes = True


# Teacher Assignment Schemas
class TeacherAssignmentCreate(BaseModel):
    teacher_id: int
    subject_id: int
    class_id: int


class TeacherAssignmentResponse(BaseModel):
    id: int
    teacher_id: int
    subject_id: int
    class_id: int
    teacher_name: str
    subject_name: str
    subject_code: str
    class_name: str
    class_section: str

    class Config:
        from_attributes = True
