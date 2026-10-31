from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
import calendar

from app.database import get_db
from app.models.academic import Student, ClassRoom, Subject
from app.models.session import ClassSession, SessionStatus, Holiday
from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.models.user import User, UserRole
from app.schemas.report import ClassAttendanceReport, StudentOverallReport, CalendarDayAttendance
from app.core.permissions import get_current_user, require_teacher_or_admin, check_teacher_subject_access, check_student_access
from app.services.attendance_calculator import calculate_class_report, calculate_student_overall_report
from app.services.excel_exporter import generate_attendance_excel

router = APIRouter(prefix="/api/reports", tags=["Reports & Analytics"])


@router.get("/class/{class_id}", response_model=ClassAttendanceReport)
def get_class_attendance_report(
    class_id: int,
    subject_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    threshold: Optional[float] = None,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Generate comprehensive class attendance report."""
    if subject_id and not check_teacher_subject_access(current_user, class_id, subject_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this subject")

    try:
        report = calculate_class_report(
            db=db,
            class_id=class_id,
            subject_id=subject_id,
            start_date=start_date,
            end_date=end_date,
            threshold=threshold
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/student/{student_id}", response_model=StudentOverallReport)
def get_student_report(
    student_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    threshold: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get student attendance report.
    Students can ONLY view their own records; teachers/admins can view any enrolled student.
    """
    if not check_student_access(current_user, student_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You are only permitted to view your own attendance records."
        )

    try:
        report = calculate_student_overall_report(
            db=db,
            student_id=student_id,
            start_date=start_date,
            end_date=end_date,
            threshold=threshold
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/student/{student_id}/calendar", response_model=List[CalendarDayAttendance])
def get_student_monthly_calendar(
    student_id: int,
    year: int,
    month: int,
    subject_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate month-by-month calendar view for student attendance.
    Shows days, holidays, cancelled classes, and attendance status.
    """
    if not check_student_access(current_user, student_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    num_days = calendar.monthrange(year, month)[1]
    start_month = date(year, month, 1)
    end_month = date(year, month, num_days)

    # Fetch holidays in this month
    holidays = db.query(Holiday).filter(
        Holiday.holiday_date >= start_month,
        Holiday.holiday_date <= end_month
    ).all()
    holiday_map = {h.holiday_date: h.name for h in holidays}

    # Fetch sessions for this student's class
    sess_query = db.query(ClassSession).filter(
        ClassSession.class_id == student.class_id,
        ClassSession.session_date >= start_month,
        ClassSession.session_date <= end_month
    )
    if subject_id:
        sess_query = sess_query.filter(ClassSession.subject_id == subject_id)

    sessions = sess_query.all()
    sessions_by_date = {s.session_date: s for s in sessions}

    # Fetch attendance records for this student
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student_id,
        AttendanceRecord.session_id.in_([s.id for s in sessions])
    ).all() if sessions else []
    record_by_session = {r.session_id: r for r in records}

    calendar_days: List[CalendarDayAttendance] = []

    for d in range(1, num_days + 1):
        curr_date = date(year, month, d)
        date_str = curr_date.isoformat()
        is_holiday = curr_date in holiday_map
        h_name = holiday_map.get(curr_date)

        sess = sessions_by_date.get(curr_date)
        status_val = None
        topic_val = None
        subj_name = None
        sess_id = None

        if sess:
            sess_id = sess.id
            topic_val = sess.topic
            subj_name = sess.subject.name if sess.subject else None
            if sess.status == SessionStatus.CANCELLED:
                status_val = "CANCELLED"
            elif sess.status == SessionStatus.HOLIDAY:
                status_val = "HOLIDAY"
            elif sess.is_attendance_submitted:
                rec = record_by_session.get(sess.id)
                status_val = rec.status.value if rec else "NOT_RECORDED"
            else:
                status_val = "NOT_RECORDED"
        elif is_holiday:
            status_val = "HOLIDAY"

        calendar_days.append(CalendarDayAttendance(
            date_str=date_str,
            day=d,
            session_id=sess_id,
            subject_name=subj_name,
            status=status_val,
            topic=topic_val,
            is_holiday=is_holiday,
            holiday_name=h_name
        ))

    return calendar_days


@router.get("/export/excel")
def export_attendance_excel(
    class_id: int,
    subject_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    Download styled official Excel attendance register.
    Restricted to authorized teachers and admins.
    """
    if not check_teacher_subject_access(current_user, class_id, subject_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to export attendance for this class and subject"
        )

    try:
        buffer, filename = generate_attendance_excel(
            db=db,
            class_id=class_id,
            subject_id=subject_id,
            teacher_name=current_user.full_name,
            start_date=start_date,
            end_date=end_date
        )

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Export failed: {str(e)}")
