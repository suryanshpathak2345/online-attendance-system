from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime

from app.database import get_db
from app.models.personal import PersonalSubject, PersonalRecord
from app.models.user import User, UserRole
from app.core.permissions import get_current_user

router = APIRouter(prefix="/api/personal", tags=["Personal Attendance Tracker"])


class PersonalSubjectCreate(BaseModel):
    name: str
    code: Optional[str] = None
    target_percentage: float = 75.0


class PersonalRecordCreate(BaseModel):
    personal_subject_id: int
    record_date: date
    status: str  # PRESENT, ABSENT, HALF_DAY, CANCELLED
    notes: Optional[str] = None


@router.get("/subjects")
def get_personal_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List personal tracking subjects for the authenticated user."""
    subjects = db.query(PersonalSubject).filter(PersonalSubject.user_id == current_user.id).all()
    results = []
    for s in subjects:
        records = s.records
        conducted = sum(1 for r in records if r.status in ["PRESENT", "ABSENT", "HALF_DAY"])
        present = sum(1 for r in records if r.status == "PRESENT")
        half_day = sum(1 for r in records if r.status == "HALF_DAY")
        absent = sum(1 for r in records if r.status == "ABSENT")
        attended = float(present) + (float(half_day) * 0.5)
        pct = round((attended / conducted) * 100, 2) if conducted > 0 else None

        results.append({
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "target_percentage": s.target_percentage,
            "conducted": conducted,
            "attended": attended,
            "absent": absent,
            "percentage": pct,
            "mode": "PERSONAL_TRACKING"
        })
    return results


@router.post("/subjects")
def create_personal_subject(
    req: PersonalSubjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(PersonalSubject).filter(
        PersonalSubject.user_id == current_user.id,
        PersonalSubject.name == req.name.strip()
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject already exists in your personal tracker")

    subj = PersonalSubject(
        user_id=current_user.id,
        name=req.name.strip(),
        code=req.code.strip() if req.code else None,
        target_percentage=req.target_percentage
    )
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return {"message": "Personal subject created", "id": subj.id, "name": subj.name, "mode": "PERSONAL_TRACKING"}


@router.get("/records")
def get_personal_records(
    personal_subject_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(PersonalRecord).join(PersonalSubject).filter(PersonalSubject.user_id == current_user.id)
    if personal_subject_id:
        query = query.filter(PersonalRecord.personal_subject_id == personal_subject_id)

    records = query.order_by(PersonalRecord.record_date.desc()).all()
    return [
        {
            "id": r.id,
            "personal_subject_id": r.personal_subject_id,
            "subject_name": r.subject.name,
            "record_date": r.record_date.isoformat(),
            "status": r.status,
            "notes": r.notes,
            "mode": "PERSONAL_TRACKING"
        }
        for r in records
    ]


@router.post("/records")
def log_personal_record(
    req: PersonalRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    subj = db.query(PersonalSubject).filter(
        PersonalSubject.id == req.personal_subject_id,
        PersonalSubject.user_id == current_user.id
    ).first()
    if not subj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personal subject not found")

    rec = db.query(PersonalRecord).filter(
        PersonalRecord.personal_subject_id == req.personal_subject_id,
        PersonalRecord.record_date == req.record_date
    ).first()

    if rec:
        rec.status = req.status
        rec.notes = req.notes
    else:
        rec = PersonalRecord(
            personal_subject_id=req.personal_subject_id,
            record_date=req.record_date,
            status=req.status,
            notes=req.notes
        )
        db.add(rec)

    db.commit()
    return {"message": "Personal record saved", "mode": "PERSONAL_TRACKING"}


@router.delete("/records/{record_id}")
def delete_personal_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = db.query(PersonalRecord).join(PersonalSubject).filter(
        PersonalRecord.id == record_id,
        PersonalSubject.user_id == current_user.id
    ).first()
    if not rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    db.delete(rec)
    db.commit()
    return {"message": "Personal entry deleted"}
