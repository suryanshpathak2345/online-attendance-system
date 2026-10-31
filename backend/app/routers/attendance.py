from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.database import get_db
from app.models.session import ClassSession, SessionStatus
from app.models.academic import Student
from app.models.attendance import AttendanceRecord, AttendanceAuditLog, AttendanceStatus
from app.models.user import User, UserRole
from app.schemas.attendance import (
    BatchAttendanceSubmission, AttendanceCorrectionRequest,
    StudentAttendanceMarkingRow, SessionAttendanceSummary,
    AttendanceRecordResponse, AttendanceAuditLogResponse
)
from app.core.permissions import get_current_user, require_teacher_or_admin, check_teacher_subject_access
from app.services.audit_service import log_attendance_change

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.get("/session/{session_id}/sheet")
def get_attendance_sheet(
    session_id: int,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    Get attendance sheet for a session.
    Lists all enrolled active students in roll number order.
    Returns status (None if not yet marked), plus absent students list.
    """
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if not check_teacher_subject_access(current_user, session.class_id, session.subject_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this class and subject")

    # Fetch active students
    students = db.query(Student).filter(
        Student.class_id == session.class_id,
        Student.is_active == True
    ).order_by(Student.roll_number).all()

    # Existing records
    existing_records = {
        r.student_id: r for r in db.query(AttendanceRecord).filter(AttendanceRecord.session_id == session_id).all()
    }

    student_rows: List[dict] = []
    absent_students: List[dict] = []
    present_count = 0
    absent_count = 0
    half_day_count = 0
    not_marked_count = 0

    for st in students:
        rec = existing_records.get(st.id)
        current_status = rec.status if rec else None
        remarks = rec.remarks if rec else None

        if current_status == AttendanceStatus.PRESENT:
            present_count += 1
        elif current_status == AttendanceStatus.ABSENT:
            absent_count += 1
            absent_students.append({
                "student_id": st.id,
                "roll_number": st.roll_number,
                "full_name": st.full_name,
                "student_identifier": st.student_identifier,
                "status": current_status,
                "remarks": remarks
            })
        elif current_status == AttendanceStatus.HALF_DAY:
            half_day_count += 1
        else:
            not_marked_count += 1

        student_rows.append({
            "student_id": st.id,
            "roll_number": st.roll_number,
            "full_name": st.full_name,
            "student_identifier": st.student_identifier,
            "status": current_status,
            "remarks": remarks,
            "record_id": rec.id if rec else None
        })

    return {
        "session_id": session.id,
        "class_id": session.class_id,
        "class_name": session.classroom.name,
        "class_section": session.classroom.section,
        "subject_id": session.subject_id,
        "subject_name": session.subject.name,
        "subject_code": session.subject.code,
        "session_date": session.session_date.isoformat(),
        "topic": session.topic,
        "is_attendance_submitted": session.is_attendance_submitted,
        "is_locked": session.is_locked,
        "total_enrolled": len(students),
        "present_count": present_count,
        "absent_count": absent_count,
        "half_day_count": half_day_count,
        "not_marked_count": not_marked_count,
        "absent_students": absent_students,
        "students": student_rows
    }


@router.post("/session/{session_id}/submit")
def submit_session_attendance(
    session_id: int,
    submission: BatchAttendanceSubmission,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    Core attendance submission workflow:
    - Validates teacher access
    - Checks session is not locked
    - Requires EVERY enrolled active student to be marked (no incomplete submissions)
    - Saves in a single atomic database transaction
    - Records audit history
    - Updates session status to CONDUCTED and marks is_attendance_submitted = True
    """
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if session.is_locked and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This session has been locked by an administrator. Edits cannot be submitted."
        )

    if not check_teacher_subject_access(current_user, session.class_id, session.subject_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to submit attendance for this class and subject."
        )

    # All active students in class
    active_students = db.query(Student).filter(
        Student.class_id == session.class_id,
        Student.is_active == True
    ).all()
    active_student_ids = {s.id for s in active_students}
    student_map = {s.id: s for s in active_students}

    # Verify every student is accounted for in submission
    submitted_student_ids = {r.student_id for r in submission.records}
    missing_student_ids = active_student_ids - submitted_student_ids

    if missing_student_ids:
        missing_names = [f"{student_map[sid].full_name} ({student_map[sid].roll_number})" for sid in missing_student_ids]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Incomplete attendance! {len(missing_student_ids)} student(s) remain NOT MARKED: {', '.join(missing_names[:5])}{'...' if len(missing_names) > 5 else ''}"
        )

    # Check for invalid student IDs
    invalid_ids = submitted_student_ids - active_student_ids
    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission contains student IDs not enrolled in this class"
        )

    # Perform atomic transaction
    try:
        # Load existing records
        existing_records = {
            r.student_id: r for r in db.query(AttendanceRecord).filter(AttendanceRecord.session_id == session_id).all()
        }

        absent_list = []
        p_cnt = 0
        a_cnt = 0
        hd_cnt = 0

        for item in submission.records:
            st = student_map[item.student_id]
            rec = existing_records.get(item.student_id)

            if rec:
                # Update existing
                prev_status = rec.status.value
                new_status = item.status.value
                if prev_status != new_status:
                    rec.status = item.status
                    rec.remarks = item.remarks
                    rec.updated_at = datetime.utcnow()
                    log_attendance_change(
                        db=db,
                        session_id=session_id,
                        student_id=st.id,
                        previous_status=prev_status,
                        new_status=new_status,
                        changed_by_user_id=current_user.id,
                        reason="Attendance submission update",
                        attendance_record_id=rec.id
                    )
            else:
                # Insert new
                new_rec = AttendanceRecord(
                    session_id=session_id,
                    student_id=st.id,
                    status=item.status,
                    remarks=item.remarks,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_rec)
                db.flush()
                log_attendance_change(
                    db=db,
                    session_id=session_id,
                    student_id=st.id,
                    previous_status="NOT_MARKED",
                    new_status=item.status.value,
                    changed_by_user_id=current_user.id,
                    reason="Initial attendance submission",
                    attendance_record_id=new_rec.id
                )

            if item.status == AttendanceStatus.PRESENT:
                p_cnt += 1
            elif item.status == AttendanceStatus.ABSENT:
                a_cnt += 1
                absent_list.append({"roll_number": st.roll_number, "full_name": st.full_name})
            elif item.status == AttendanceStatus.HALF_DAY:
                hd_cnt += 1

        session.is_attendance_submitted = True
        session.status = SessionStatus.CONDUCTED
        session.submitted_at = datetime.utcnow()

        db.commit()

        return {
            "success": True,
            "message": f"Attendance successfully submitted for session on {session.session_date.isoformat()}.",
            "total_marked": len(submission.records),
            "present_count": p_cnt,
            "absent_count": a_cnt,
            "half_day_count": hd_cnt,
            "absent_students": absent_list
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit attendance: {str(e)}"
        )


@router.patch("/record/{record_id}/correct")
def correct_attendance_record(
    record_id: int,
    req: AttendanceCorrectionRequest,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """
    Section 12: Correct previously submitted attendance for an individual student.
    Maintains an audit trail: previous status, new status, changed by, timestamp, reason.
    """
    record = db.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found")

    session = record.session
    if session.is_locked and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session is locked by administrator. Attendance cannot be modified."
        )

    if not check_teacher_subject_access(current_user, session.class_id, session.subject_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify attendance for this class and subject"
        )

    previous_status = record.status.value
    new_status = req.new_status.value

    if previous_status == new_status:
        return {"message": "Status unchanged", "record_id": record.id, "status": record.status}

    record.status = req.new_status
    record.updated_at = datetime.utcnow()

    # Create audit log
    audit_log = log_attendance_change(
        db=db,
        session_id=session.id,
        student_id=record.student_id,
        previous_status=previous_status,
        new_status=new_status,
        changed_by_user_id=current_user.id,
        reason=req.reason or "Teacher attendance correction",
        attendance_record_id=record.id
    )

    db.commit()
    db.refresh(record)

    student = record.student
    return {
        "success": True,
        "message": f"Updated attendance for {student.full_name} ({student.roll_number}) from {previous_status} to {new_status}.",
        "record_id": record.id,
        "student_id": student.id,
        "roll_number": student.roll_number,
        "student_name": student.full_name,
        "previous_status": previous_status,
        "new_status": new_status,
        "changed_by": current_user.full_name,
        "changed_at": audit_log.changed_at.isoformat()
    }


@router.get("/session/{session_id}/audit-logs", response_model=List[AttendanceAuditLogResponse])
def get_session_audit_logs(
    session_id: int,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Retrieve audit trail for all changes to this session's attendance."""
    session = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if not check_teacher_subject_access(current_user, session.class_id, session.subject_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    logs = db.query(AttendanceAuditLog).filter(
        AttendanceAuditLog.session_id == session_id
    ).order_by(AttendanceAuditLog.changed_at.desc()).all()

    results = []
    for l in logs:
        results.append(AttendanceAuditLogResponse(
            id=l.id,
            session_id=l.session_id,
            student_id=l.student_id,
            student_name=l.student.full_name if l.student else "Unknown",
            student_roll=l.student.roll_number if l.student else "---",
            previous_status=l.previous_status,
            new_status=l.new_status,
            reason=l.reason,
            changed_by_user_id=l.changed_by_user_id,
            changed_by_name=l.changed_by.full_name if l.changed_by else "System",
            changed_at=l.changed_at
        ))
    return results
