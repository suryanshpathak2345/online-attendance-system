from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.attendance import AttendanceStatus


class SingleStudentAttendance(BaseModel):
    student_id: int
    status: AttendanceStatus
    remarks: Optional[str] = None


class BatchAttendanceSubmission(BaseModel):
    records: List[SingleStudentAttendance]


class AttendanceCorrectionRequest(BaseModel):
    new_status: AttendanceStatus
    reason: Optional[str] = None


class StudentAttendanceMarkingRow(BaseModel):
    student_id: int
    roll_number: str
    full_name: str
    student_identifier: str
    status: Optional[AttendanceStatus] = None
    remarks: Optional[str] = None


class SessionAttendanceSummary(BaseModel):
    session_id: int
    total_enrolled: int
    present_count: int
    absent_count: int
    half_day_count: int
    not_marked_count: int
    absent_students: List[StudentAttendanceMarkingRow]


class AttendanceRecordResponse(BaseModel):
    id: int
    session_id: int
    student_id: int
    student_name: str
    student_roll: str
    status: AttendanceStatus
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AttendanceAuditLogResponse(BaseModel):
    id: int
    session_id: int
    student_id: int
    student_name: str
    student_roll: str
    previous_status: str
    new_status: str
    reason: Optional[str] = None
    changed_by_user_id: int
    changed_by_name: str
    changed_at: datetime

    class Config:
        from_attributes = True
