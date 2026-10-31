from datetime import date, timedelta
from app.services.attendance_calculator import (
    calculate_percentage,
    calculate_student_subject_attendance,
    calculate_student_overall_report,
    calculate_class_report
)
from app.models.session import ClassSession, SessionStatus
from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.models.academic import Subject
from app.config import settings


def test_zero_conducted_sessions_returns_none():
    """When no conducted sessions exist, calculation returns None (not 0 or ZeroDivisionError)."""
    assert calculate_percentage(0, 0) is None
    assert calculate_percentage(5, 0) is None


def test_standard_percentage_calculation():
    """Verify standard formula (attended / conducted) * 100."""
    assert calculate_percentage(15, 20) == 75.0
    assert calculate_percentage(17, 20) == 85.0
    assert calculate_percentage(1, 3) == 33.33


def test_half_day_and_holiday_exclusion(db_session, test_data):
    """
    Test that:
    1. HALF_DAY counts as 0.5 (configured weight).
    2. HOLIDAY sessions are completely excluded from conducted denominator.
    3. CANCELLED sessions are completely excluded.
    """
    classroom = test_data["classroom"]
    subject = test_data["subject"]
    teacher = test_data["teacher1"]
    student = test_data["student1"]

    # 1. Conducted session: Student PRESENT (1.0)
    s1 = ClassSession(
        class_id=classroom.id, subject_id=subject.id, teacher_id=teacher.id,
        session_date=date.today() - timedelta(days=5), status=SessionStatus.CONDUCTED,
        is_attendance_submitted=True
    )
    # 2. Conducted session: Student HALF_DAY (0.5)
    s2 = ClassSession(
        class_id=classroom.id, subject_id=subject.id, teacher_id=teacher.id,
        session_date=date.today() - timedelta(days=4), status=SessionStatus.CONDUCTED,
        is_attendance_submitted=True
    )
    # 3. Conducted session: Student ABSENT (0.0)
    s3 = ClassSession(
        class_id=classroom.id, subject_id=subject.id, teacher_id=teacher.id,
        session_date=date.today() - timedelta(days=3), status=SessionStatus.CONDUCTED,
        is_attendance_submitted=True
    )
    # 4. Cancelled session (Must be excluded)
    s4 = ClassSession(
        class_id=classroom.id, subject_id=subject.id, teacher_id=teacher.id,
        session_date=date.today() - timedelta(days=2), status=SessionStatus.CANCELLED,
        is_attendance_submitted=False
    )
    # 5. Holiday session (Must be excluded)
    s5 = ClassSession(
        class_id=classroom.id, subject_id=subject.id, teacher_id=teacher.id,
        session_date=date.today() - timedelta(days=1), status=SessionStatus.HOLIDAY,
        is_attendance_submitted=False
    )
    db_session.add_all([s1, s2, s3, s4, s5])
    db_session.flush()

    # Add attendance records for conducted sessions
    r1 = AttendanceRecord(session_id=s1.id, student_id=student.id, status=AttendanceStatus.PRESENT)
    r2 = AttendanceRecord(session_id=s2.id, student_id=student.id, status=AttendanceStatus.HALF_DAY)
    r3 = AttendanceRecord(session_id=s3.id, student_id=student.id, status=AttendanceStatus.ABSENT)
    db_session.add_all([r1, r2, r3])
    db_session.commit()

    # Total conducted sessions should be exactly 3 (excluding s4 and s5)
    # Attended = 1.0 (s1) + 0.5 (s2) + 0.0 (s3) = 1.5
    # Expected percentage = (1.5 / 3) * 100 = 50.0%
    summary = calculate_student_subject_attendance(
        db=db_session,
        student_id=student.id,
        subject_id=subject.id,
        class_id=classroom.id
    )

    assert summary.conducted_sessions == 3
    assert summary.attended_sessions == 1.5
    assert summary.absent_sessions == 1
    assert summary.half_day_sessions == 1
    assert summary.attendance_percentage == 50.0
    assert summary.is_below_threshold is True  # 50.0 < 75.0


def test_combined_overall_calculation_never_averages_percentages(db_session, test_data):
    """
    Combined attendance must equal total attended across all subjects divided by total conducted,
    NEVER the mathematical average of the individual subject percentages.
    
    Subject A: 1 conducted, 1 attended -> 100%
    Subject B: 3 conducted, 0 attended -> 0%
    Average of percentages would be (100 + 0) / 2 = 50% (WRONG)
    True combined attendance = (1 + 0) / (1 + 3) = 1 / 4 = 25% (CORRECT)
    """
    classroom = test_data["classroom"]
    teacher = test_data["teacher1"]
    student = test_data["student1"]

    sub_a = test_data["subject"]  # Subject 1
    sub_b = Subject(name="Subject B", code="SUB-B", class_id=classroom.id)
    db_session.add(sub_b)
    db_session.flush()

    # Subject A: 1 session, present
    sa1 = ClassSession(
        class_id=classroom.id, subject_id=sub_a.id, teacher_id=teacher.id,
        session_date=date.today() - timedelta(days=4), status=SessionStatus.CONDUCTED,
        is_attendance_submitted=True
    )
    db_session.add(sa1)
    db_session.flush()
    db_session.add(AttendanceRecord(session_id=sa1.id, student_id=student.id, status=AttendanceStatus.PRESENT))

    # Subject B: 3 sessions, all absent
    for d in range(1, 4):
        sb = ClassSession(
            class_id=classroom.id, subject_id=sub_b.id, teacher_id=teacher.id,
            session_date=date.today() - timedelta(days=d), status=SessionStatus.CONDUCTED,
            is_attendance_submitted=True
        )
        db_session.add(sb)
        db_session.flush()
        db_session.add(AttendanceRecord(session_id=sb.id, student_id=student.id, status=AttendanceStatus.ABSENT))

    db_session.commit()

    report = calculate_student_overall_report(db=db_session, student_id=student.id)
    assert report.total_conducted == 4
    assert report.total_attended == 1.0
    assert report.overall_percentage == 25.0
