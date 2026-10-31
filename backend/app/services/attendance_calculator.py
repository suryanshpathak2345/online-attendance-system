from typing import Optional, List, Dict, Tuple
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.academic import ClassRoom, Student, Subject
from app.models.session import ClassSession, SessionStatus
from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.schemas.report import (
    StudentSubjectSummary, StudentOverallReport,
    ClassAttendanceReportRow, ClassAttendanceReport,
    CalendarDayAttendance
)
from app.config import settings


def calculate_percentage(attended: float, conducted: int) -> Optional[float]:
    """Calculate percentage rounded to 2 decimal places. Returns None if conducted == 0."""
    if conducted == 0:
        return None
    return round((attended / conducted) * 100.0, 2)


def get_conducted_sessions_query(
    db: Session,
    class_id: int,
    subject_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """
    Query for valid conducted sessions where attendance was finalized.
    Excludes CANCELLED, HOLIDAY, and unsubmitted sessions.
    """
    filters = [
        ClassSession.class_id == class_id,
        ClassSession.status == SessionStatus.CONDUCTED,
        ClassSession.is_attendance_submitted == True
    ]
    if subject_id:
        filters.append(ClassSession.subject_id == subject_id)
    if start_date:
        filters.append(ClassSession.session_date >= start_date)
    if end_date:
        filters.append(ClassSession.session_date <= end_date)

    return db.query(ClassSession).filter(and_(*filters))


def calculate_student_subject_attendance(
    db: Session,
    student_id: int,
    subject_id: int,
    class_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    threshold: Optional[float] = None
) -> StudentSubjectSummary:
    if threshold is None:
        threshold = settings.default_attendance_threshold

    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    subject_name = subject.name if subject else "Unknown Subject"
    subject_code = subject.code if subject else "---"

    sessions = get_conducted_sessions_query(db, class_id, subject_id, start_date, end_date).all()
    conducted_count = len(sessions)

    if conducted_count == 0:
        return StudentSubjectSummary(
            subject_id=subject_id,
            subject_name=subject_name,
            subject_code=subject_code,
            conducted_sessions=0,
            attended_sessions=0.0,
            absent_sessions=0,
            half_day_sessions=0,
            attendance_percentage=None,
            threshold=threshold,
            is_below_threshold=False
        )

    session_ids = [s.id for s in sessions]
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.student_id == student_id,
        AttendanceRecord.session_id.in_(session_ids)
    ).all()

    present_count = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
    absent_count = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
    half_day_count = sum(1 for r in records if r.status == AttendanceStatus.HALF_DAY)

    half_weight = settings.half_day_weight if settings.allow_half_day else 0.0
    attended_total = float(present_count) + (float(half_day_count) * half_weight)

    pct = calculate_percentage(attended_total, conducted_count)
    is_below = (pct is not None) and (pct < threshold)

    return StudentSubjectSummary(
        subject_id=subject_id,
        subject_name=subject_name,
        subject_code=subject_code,
        conducted_sessions=conducted_count,
        attended_sessions=attended_total,
        absent_sessions=absent_count,
        half_day_sessions=half_day_count,
        attendance_percentage=pct,
        threshold=threshold,
        is_below_threshold=is_below
    )


def calculate_student_overall_report(
    db: Session,
    student_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    threshold: Optional[float] = None
) -> StudentOverallReport:
    if threshold is None:
        threshold = settings.default_attendance_threshold

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError(f"Student with id {student_id} not found")

    classroom = student.classroom
    subjects = db.query(Subject).filter(Subject.class_id == student.class_id).all()

    subject_summaries: List[StudentSubjectSummary] = []
    total_conducted = 0
    total_attended = 0.0
    total_absent = 0
    total_half_day = 0

    for subj in subjects:
        subj_summary = calculate_student_subject_attendance(
            db=db,
            student_id=student.id,
            subject_id=subj.id,
            class_id=student.class_id,
            start_date=start_date,
            end_date=end_date,
            threshold=threshold
        )
        subject_summaries.append(subj_summary)
        total_conducted += subj_summary.conducted_sessions
        total_attended += subj_summary.attended_sessions
        total_absent += subj_summary.absent_sessions
        total_half_day += subj_summary.half_day_sessions

    overall_pct = calculate_percentage(total_attended, total_conducted)
    is_below = (overall_pct is not None) and (overall_pct < threshold)

    return StudentOverallReport(
        student_id=student.id,
        roll_number=student.roll_number,
        full_name=student.full_name,
        class_id=classroom.id,
        class_name=classroom.name,
        class_section=classroom.section,
        total_conducted=total_conducted,
        total_attended=total_attended,
        total_absent=total_absent,
        total_half_day=total_half_day,
        overall_percentage=overall_pct,
        threshold=threshold,
        is_below_threshold=is_below,
        subject_summaries=subject_summaries
    )


def calculate_class_report(
    db: Session,
    class_id: int,
    subject_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    threshold: Optional[float] = None
) -> ClassAttendanceReport:
    if threshold is None:
        threshold = settings.default_attendance_threshold

    classroom = db.query(ClassRoom).filter(ClassRoom.id == class_id).first()
    if not classroom:
        raise ValueError(f"Class with id {class_id} not found")

    subject_name = None
    if subject_id:
        subj = db.query(Subject).filter(Subject.id == subject_id).first()
        if subj:
            subject_name = f"{subj.name} ({subj.code})"

    sessions = get_conducted_sessions_query(db, class_id, subject_id, start_date, end_date).all()
    conducted_sessions_count = len(sessions)
    session_ids = [s.id for s in sessions]

    students = db.query(Student).filter(
        Student.class_id == class_id,
        Student.is_active == True
    ).order_by(Student.roll_number).all()

    student_rows: List[ClassAttendanceReportRow] = []
    total_percentages: List[float] = []
    low_attendance_count = 0

    half_weight = settings.half_day_weight if settings.allow_half_day else 0.0

    for st in students:
        if conducted_sessions_count == 0:
            row = ClassAttendanceReportRow(
                student_id=st.id,
                roll_number=st.roll_number,
                full_name=st.full_name,
                conducted_sessions=0,
                attended_sessions=0.0,
                absent_sessions=0,
                half_day_sessions=0,
                attendance_percentage=None,
                is_below_threshold=False
            )
        else:
            records = db.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == st.id,
                AttendanceRecord.session_id.in_(session_ids)
            ).all()

            p_cnt = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
            a_cnt = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
            hd_cnt = sum(1 for r in records if r.status == AttendanceStatus.HALF_DAY)
            att_total = float(p_cnt) + (float(hd_cnt) * half_weight)
            pct = calculate_percentage(att_total, conducted_sessions_count)
            is_below = (pct is not None) and (pct < threshold)
            if is_below:
                low_attendance_count += 1
            if pct is not None:
                total_percentages.append(pct)

            row = ClassAttendanceReportRow(
                student_id=st.id,
                roll_number=st.roll_number,
                full_name=st.full_name,
                conducted_sessions=conducted_sessions_count,
                attended_sessions=att_total,
                absent_sessions=a_cnt,
                half_day_sessions=hd_cnt,
                attendance_percentage=pct,
                is_below_threshold=is_below
            )
        student_rows.append(row)

    avg_pct = round(sum(total_percentages) / len(total_percentages), 2) if total_percentages else None

    return ClassAttendanceReport(
        class_id=classroom.id,
        class_name=classroom.name,
        class_section=classroom.section,
        academic_year=classroom.academic_year,
        subject_id=subject_id,
        subject_name=subject_name,
        start_date=start_date,
        end_date=end_date,
        threshold=threshold,
        total_conducted_sessions=conducted_sessions_count,
        average_attendance_percentage=avg_pct,
        students_count=len(students),
        low_attendance_count=low_attendance_count,
        student_rows=student_rows
    )
