import pytest
from fastapi import HTTPException, status
from app.routers.attendance import submit_session_attendance, correct_attendance_record
from app.routers.reports import get_student_report, export_attendance_excel
from app.schemas.attendance import BatchAttendanceSubmission, SingleStudentAttendance, AttendanceCorrectionRequest
from app.models.attendance import AttendanceStatus


def test_teacher_cannot_submit_unassigned_class(db_session, test_data):
    """Teacher 2 is not assigned to this class and subject, so submission must be forbidden (403)."""
    teacher2 = test_data["teacher2"]
    session = test_data["session"]

    submission = BatchAttendanceSubmission(
        records=[
            SingleStudentAttendance(student_id=test_data["student1"].id, status=AttendanceStatus.PRESENT),
            SingleStudentAttendance(student_id=test_data["student2"].id, status=AttendanceStatus.PRESENT)
        ]
    )

    with pytest.raises(HTTPException) as exc:
        submit_session_attendance(
            session_id=session.id,
            submission=submission,
            current_user=teacher2,
            db=db_session
        )

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "not authorized" in exc.value.detail.lower()


def test_student_cannot_access_other_student_records(db_session, test_data):
    """Student 1 cannot access Student 2's attendance report (403)."""
    stu_user1 = test_data["stu_user1"]

    with pytest.raises(HTTPException) as exc:
        get_student_report(
            student_id=test_data["student2"].id,
            current_user=stu_user1,
            db=db_session
        )

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "only permitted to view your own" in exc.value.detail.lower()


def test_student_can_access_own_records(db_session, test_data):
    """Student 1 CAN access their own attendance report."""
    stu_user1 = test_data["stu_user1"]

    report = get_student_report(
        student_id=test_data["student1"].id,
        current_user=stu_user1,
        db=db_session
    )
    assert report.student_id == test_data["student1"].id
    assert report.roll_number == test_data["student1"].roll_number


def test_unauthorized_user_cannot_export_excel(db_session, test_data):
    """Student cannot export Excel reports."""
    stu_user1 = test_data["stu_user1"]

    with pytest.raises(HTTPException) as exc:
        export_attendance_excel(
            class_id=test_data["classroom"].id,
            subject_id=test_data["subject"].id,
            current_user=stu_user1,
            db=db_session
        )

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
