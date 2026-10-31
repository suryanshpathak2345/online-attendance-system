from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.session import ClassSession, SessionStatus
from app.models.academic import ClassRoom, Subject
from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.models.user import User, UserRole
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse
from app.core.permissions import get_current_user, require_teacher_or_admin, check_teacher_subject_access

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    class_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    session_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    teacher_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ClassSession)

    if class_id:
        query = query.filter(ClassSession.class_id == class_id)
    if subject_id:
        query = query.filter(ClassSession.subject_id == subject_id)
    if session_date:
        query = query.filter(ClassSession.session_date == session_date)
    if start_date:
        query = query.filter(ClassSession.session_date >= start_date)
    if end_date:
        query = query.filter(ClassSession.session_date <= end_date)
    if teacher_id:
        query = query.filter(ClassSession.teacher_id == teacher_id)

    sessions = query.order_by(ClassSession.session_date.desc(), ClassSession.id.desc()).all()
    results = []

    for s in sessions:
        p_cnt = 0
        a_cnt = 0
        hd_cnt = 0
        tot_cnt = 0
        if s.is_attendance_submitted:
            records = db.query(AttendanceRecord).filter(AttendanceRecord.session_id == s.id).all()
            tot_cnt = len(records)
            p_cnt = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
            a_cnt = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
            hd_cnt = sum(1 for r in records if r.status == AttendanceStatus.HALF_DAY)

        results.append(SessionResponse(
            id=s.id,
            class_id=s.class_id,
            subject_id=s.subject_id,
            teacher_id=s.teacher_id,
            session_date=s.session_date,
            start_time=s.start_time,
            end_time=s.end_time,
            topic=s.topic,
            status=s.status,
            is_attendance_submitted=s.is_attendance_submitted,
            is_locked=s.is_locked,
            submitted_at=s.submitted_at,
            created_at=s.created_at,
            class_name=s.classroom.name if s.classroom else None,
            class_section=s.classroom.section if s.classroom else None,
            subject_name=s.subject.name if s.subject else None,
            subject_code=s.subject.code if s.subject else None,
            teacher_name=s.teacher.full_name if s.teacher else None,
            total_students=tot_cnt,
            present_count=p_cnt,
            absent_count=a_cnt,
            half_day_count=hd_cnt
        ))

    return results


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    req: SessionCreate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    """Create a new class session. Teacher must be assigned unless Admin."""
    classroom = db.query(ClassRoom).filter(ClassRoom.id == req.class_id).first()
    subject = db.query(Subject).filter(Subject.id == req.subject_id, Subject.class_id == req.class_id).first()
    if not classroom or not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class or Subject not found")

    teacher_id = req.teacher_id if (current_user.role == UserRole.ADMIN and req.teacher_id) else current_user.id

    if not check_teacher_subject_access(current_user, req.class_id, req.subject_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to conduct session for this subject")

    session = ClassSession(
        class_id=req.class_id,
        subject_id=req.subject_id,
        teacher_id=teacher_id,
        session_date=req.session_date,
        start_time=req.start_time,
        end_time=req.end_time,
        topic=req.topic.strip() if req.topic else None,
        status=req.status
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionResponse(
        id=session.id,
        class_id=session.class_id,
        subject_id=session.subject_id,
        teacher_id=session.teacher_id,
        session_date=session.session_date,
        start_time=session.start_time,
        end_time=session.end_time,
        topic=session.topic,
        status=session.status,
        is_attendance_submitted=session.is_attendance_submitted,
        is_locked=session.is_locked,
        submitted_at=session.submitted_at,
        created_at=session.created_at,
        class_name=classroom.name,
        class_section=classroom.section,
        subject_name=subject.name,
        subject_code=subject.code,
        teacher_name=session.teacher.full_name if session.teacher else None,
        total_students=0,
        present_count=0,
        absent_count=0,
        half_day_count=0
    )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    s = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    records = db.query(AttendanceRecord).filter(AttendanceRecord.session_id == s.id).all()
    p_cnt = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
    a_cnt = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
    hd_cnt = sum(1 for r in records if r.status == AttendanceStatus.HALF_DAY)

    return SessionResponse(
        id=s.id,
        class_id=s.class_id,
        subject_id=s.subject_id,
        teacher_id=s.teacher_id,
        session_date=s.session_date,
        start_time=s.start_time,
        end_time=s.end_time,
        topic=s.topic,
        status=s.status,
        is_attendance_submitted=s.is_attendance_submitted,
        is_locked=s.is_locked,
        submitted_at=s.submitted_at,
        created_at=s.created_at,
        class_name=s.classroom.name if s.classroom else None,
        class_section=s.classroom.section if s.classroom else None,
        subject_name=s.subject.name if s.subject else None,
        subject_code=s.subject.code if s.subject else None,
        teacher_name=s.teacher.full_name if s.teacher else None,
        total_students=len(records),
        present_count=p_cnt,
        absent_count=a_cnt,
        half_day_count=hd_cnt
    )


@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    req: SessionUpdate,
    current_user: User = Depends(require_teacher_or_admin),
    db: Session = Depends(get_db)
):
    s = db.query(ClassSession).filter(ClassSession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if s.is_locked and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Session is locked by administrator")

    if not check_teacher_subject_access(current_user, s.class_id, s.subject_id, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this session")

    if req.session_date is not None:
        s.session_date = req.session_date
    if req.start_time is not None:
        s.start_time = req.start_time
    if req.end_time is not None:
        s.end_time = req.end_time
    if req.topic is not None:
        s.topic = req.topic.strip()
    if req.status is not None:
        s.status = req.status
    if req.is_locked is not None and current_user.role == UserRole.ADMIN:
        s.is_locked = req.is_locked

    db.commit()
    db.refresh(s)

    records = db.query(AttendanceRecord).filter(AttendanceRecord.session_id == s.id).all()
    p_cnt = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
    a_cnt = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
    hd_cnt = sum(1 for r in records if r.status == AttendanceStatus.HALF_DAY)

    return SessionResponse(
        id=s.id,
        class_id=s.class_id,
        subject_id=s.subject_id,
        teacher_id=s.teacher_id,
        session_date=s.session_date,
        start_time=s.start_time,
        end_time=s.end_time,
        topic=s.topic,
        status=s.status,
        is_attendance_submitted=s.is_attendance_submitted,
        is_locked=s.is_locked,
        submitted_at=s.submitted_at,
        created_at=s.created_at,
        class_name=s.classroom.name if s.classroom else None,
        class_section=s.classroom.section if s.classroom else None,
        subject_name=s.subject.name if s.subject else None,
        subject_code=s.subject.code if s.subject else None,
        teacher_name=s.teacher.full_name if s.teacher else None,
        total_students=len(records),
        present_count=p_cnt,
        absent_count=a_cnt,
        half_day_count=hd_cnt
    )
