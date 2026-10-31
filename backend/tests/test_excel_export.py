import openpyxl
from datetime import date, timedelta
from app.services.excel_exporter import generate_attendance_excel
from app.models.session import ClassSession, SessionStatus
from app.models.attendance import AttendanceRecord, AttendanceStatus


def test_excel_export_generation_and_layout(db_session, test_data):
    classroom = test_data["classroom"]
    subject = test_data["subject"]
    teacher = test_data["teacher1"]
    student1 = test_data["student1"]
    student2 = test_data["student2"]

    # 1. Conducted Session
    s1 = ClassSession(
        class_id=classroom.id, subject_id=subject.id, teacher_id=teacher.id,
        session_date=date.today() - timedelta(days=2), status=SessionStatus.CONDUCTED,
        is_attendance_submitted=True
    )
    # 2. Cancelled Session
    s2 = ClassSession(
        class_id=classroom.id, subject_id=subject.id, teacher_id=teacher.id,
        session_date=date.today() - timedelta(days=1), status=SessionStatus.CANCELLED,
        is_attendance_submitted=False
    )
    db_session.add_all([s1, s2])
    db_session.flush()

    # Attendance: Student 1 = PRESENT, Student 2 = ABSENT
    r1 = AttendanceRecord(session_id=s1.id, student_id=student1.id, status=AttendanceStatus.PRESENT)
    r2 = AttendanceRecord(session_id=s1.id, student_id=student2.id, status=AttendanceStatus.ABSENT)
    db_session.add_all([r1, r2])
    db_session.commit()

    # Generate Excel
    buffer, filename = generate_attendance_excel(
        db=db_session,
        class_id=classroom.id,
        subject_id=subject.id,
        teacher_name=teacher.full_name
    )

    assert filename.endswith(".xlsx")
    assert "Computer_Science" in filename or "Algorithms" in filename

    # Load workbook from buffer and inspect
    wb = openpyxl.load_workbook(buffer)
    ws = wb.active
    assert ws.title == "Attendance Register"

    # Title check
    title_cell = ws["A1"].value
    assert "Attendance Register" in title_cell

    # Check for student rolls in column A
    rolls = [ws.cell(row=r, column=1).value for r in range(8, 12) if ws.cell(row=r, column=1).value]
    assert "STU-01" in rolls
    assert "STU-02" in rolls
