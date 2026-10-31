import pytest
from fastapi import HTTPException, status
from app.routers.attendance import (
    get_attendance_sheet,
    submit_session_attendance,
    correct_attendance_record,
    get_session_audit_logs
)
from app.schemas.attendance import (
    BatchAttendanceSubmission,
    SingleStudentAttendance,
    AttendanceCorrectionRequest
)
from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.models.session import SessionStatus


def test_get_attendance_sheet(db_session, test_data):
    teacher = test_data["teacher1"]
    session = test_data["session"]

    sheet = get_attendance_sheet(session_id=session.id, current_user=teacher, db=db_session)
    assert sheet["session_id"] == session.id
    assert sheet["total_enrolled"] == 2
    assert len(sheet["students"]) == 2
    assert sheet["students"][0]["status"] is None
    assert sheet["not_marked_count"] == 2


def test_reject_incomplete_attendance(db_session, test_data):
    """If any enrolled student remains not marked, submission must raise 422 Unprocessable Entity."""
    teacher = test_data["teacher1"]
    session = test_data["session"]

    incomplete_submission = BatchAttendanceSubmission(
        records=[
            SingleStudentAttendance(student_id=test_data["student1"].id, status=AttendanceStatus.PRESENT)
            # Student 2 is missing!
        ]
    )

    with pytest.raises(HTTPException) as exc:
        submit_session_attendance(
            session_id=session.id,
            submission=incomplete_submission,
            current_user=teacher,
            db=db_session
        )

    assert exc.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Incomplete attendance" in exc.value.detail


def test_submit_valid_attendance_with_all_present_and_absent(db_session, test_data):
    teacher = test_data["teacher1"]
    session = test_data["session"]

    submission = BatchAttendanceSubmission(
        records=[
            SingleStudentAttendance(student_id=test_data["student1"].id, status=AttendanceStatus.PRESENT),
            SingleStudentAttendance(student_id=test_data["student2"].id, status=AttendanceStatus.ABSENT, remarks="Sick leave")
        ]
    )

    res = submit_session_attendance(
        session_id=session.id,
        submission=submission,
        current_user=teacher,
        db=db_session
    )

    assert res["success"] is True
    assert res["present_count"] == 1
    assert res["absent_count"] == 1
    assert len(res["absent_students"]) == 1
    assert res["absent_students"][0]["roll_number"] == test_data["student2"].roll_number

    db_session.refresh(session)
    assert session.is_attendance_submitted is True
    assert session.status == SessionStatus.CONDUCTED


def test_prevent_duplicate_attendance_records(db_session, test_data):
    teacher = test_data["teacher1"]
    session = test_data["session"]

    submission1 = BatchAttendanceSubmission(
        records=[
            SingleStudentAttendance(student_id=test_data["student1"].id, status=AttendanceStatus.PRESENT),
            SingleStudentAttendance(student_id=test_data["student2"].id, status=AttendanceStatus.PRESENT)
        ]
    )
    submit_session_attendance(session.id, submission1, teacher, db_session)
    assert db_session.query(AttendanceRecord).filter(AttendanceRecord.session_id == session.id).count() == 2

    # Second submission updates rather than inserting duplicates
    submission2 = BatchAttendanceSubmission(
        records=[
            SingleStudentAttendance(student_id=test_data["student1"].id, status=AttendanceStatus.PRESENT),
            SingleStudentAttendance(student_id=test_data["student2"].id, status=AttendanceStatus.ABSENT)
        ]
    )
    submit_session_attendance(session.id, submission2, teacher, db_session)
    assert db_session.query(AttendanceRecord).filter(AttendanceRecord.session_id == session.id).count() == 2


def test_attendance_correction_and_audit_history(db_session, test_data):
    teacher = test_data["teacher1"]
    session = test_data["session"]

    # Initial submit
    submit_session_attendance(
        session_id=session.id,
        submission=BatchAttendanceSubmission(
            records=[
                SingleStudentAttendance(student_id=test_data["student1"].id, status=AttendanceStatus.PRESENT),
                SingleStudentAttendance(student_id=test_data["student2"].id, status=AttendanceStatus.ABSENT)
            ]
        ),
        current_user=teacher,
        db=db_session
    )

    rec2 = db_session.query(AttendanceRecord).filter(
        AttendanceRecord.session_id == session.id,
        AttendanceRecord.student_id == test_data["student2"].id
    ).first()

    # Correct status
    correction_req = AttendanceCorrectionRequest(
        new_status=AttendanceStatus.PRESENT,
        reason="Official robotics symposium duty"
    )
    corr_res = correct_attendance_record(
        record_id=rec2.id,
        req=correction_req,
        current_user=teacher,
        db=db_session
    )

    assert corr_res["previous_status"] == "ABSENT"
    assert corr_res["new_status"] == "PRESENT"

    # Audit history check
    logs = get_session_audit_logs(session_id=session.id, current_user=teacher, db=db_session)
    assert len(logs) >= 1
    assert logs[0].previous_status == "ABSENT"
    assert logs[0].new_status == "PRESENT"
    assert "robotics" in logs[0].reason.lower()
