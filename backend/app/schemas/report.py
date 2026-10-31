from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date
from app.models.attendance import AttendanceStatus


class StudentSubjectSummary(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: str
    conducted_sessions: int
    attended_sessions: float
    absent_sessions: int
    half_day_sessions: int
    attendance_percentage: Optional[float]
    threshold: float
    is_below_threshold: bool


class StudentOverallReport(BaseModel):
    student_id: int
    roll_number: str
    full_name: str
    class_id: int
    class_name: str
    class_section: str
    total_conducted: int
    total_attended: float
    total_absent: int
    total_half_day: int
    overall_percentage: Optional[float]
    threshold: float
    is_below_threshold: bool
    subject_summaries: List[StudentSubjectSummary]


class ClassAttendanceReportRow(BaseModel):
    student_id: int
    roll_number: str
    full_name: str
    conducted_sessions: int
    attended_sessions: float
    absent_sessions: int
    half_day_sessions: int
    attendance_percentage: Optional[float]
    is_below_threshold: bool


class ClassAttendanceReport(BaseModel):
    class_id: int
    class_name: str
    class_section: str
    academic_year: str
    subject_id: Optional[int] = None
    subject_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    threshold: float
    total_conducted_sessions: int
    average_attendance_percentage: Optional[float]
    students_count: int
    low_attendance_count: int
    student_rows: List[ClassAttendanceReportRow]


class CalendarDayAttendance(BaseModel):
    date_str: str  # YYYY-MM-DD
    day: int
    session_id: Optional[int] = None
    subject_name: Optional[str] = None
    status: Optional[str] = None  # PRESENT, ABSENT, HALF_DAY, HOLIDAY, CANCELLED, NOT_RECORDED
    topic: Optional[str] = None
    is_holiday: bool = False
    holiday_name: Optional[str] = None
