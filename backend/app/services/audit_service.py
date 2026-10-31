from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.attendance import AttendanceAuditLog


def log_attendance_change(
    db: Session,
    session_id: int,
    student_id: int,
    previous_status: str,
    new_status: str,
    changed_by_user_id: int,
    reason: Optional[str] = None,
    attendance_record_id: Optional[int] = None
) -> AttendanceAuditLog:
    """Create an immutable audit log entry for attendance modifications."""
    audit_entry = AttendanceAuditLog(
        attendance_record_id=attendance_record_id,
        session_id=session_id,
        student_id=student_id,
        previous_status=previous_status,
        new_status=new_status,
        reason=reason,
        changed_by_user_id=changed_by_user_id,
        changed_at=datetime.utcnow()
    )
    db.add(audit_entry)
    return audit_entry
