from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime
from app.models.session import SessionStatus, HolidayType


# Class Session Schemas
class SessionBase(BaseModel):
    class_id: int
    subject_id: int
    session_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    topic: Optional[str] = None
    status: SessionStatus = SessionStatus.SCHEDULED


class SessionCreate(SessionBase):
    teacher_id: Optional[int] = None  # Admin can specify; teacher defaults to current_user


class SessionUpdate(BaseModel):
    session_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    topic: Optional[str] = None
    status: Optional[SessionStatus] = None
    is_locked: Optional[bool] = None


class SessionResponse(SessionBase):
    id: int
    teacher_id: int
    is_attendance_submitted: bool
    is_locked: bool
    submitted_at: Optional[datetime] = None
    created_at: datetime
    class_name: Optional[str] = None
    class_section: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    teacher_name: Optional[str] = None
    total_students: Optional[int] = 0
    present_count: Optional[int] = 0
    absent_count: Optional[int] = 0
    half_day_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Holiday Schemas
class HolidayBase(BaseModel):
    name: str
    holiday_date: date
    holiday_type: HolidayType = HolidayType.INSTITUTIONAL
    description: Optional[str] = None


class HolidayCreate(HolidayBase):
    pass


class HolidayResponse(HolidayBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
