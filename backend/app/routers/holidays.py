from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.session import Holiday, HolidayType
from app.models.user import User
from app.schemas.session import HolidayCreate, HolidayResponse
from app.core.permissions import get_current_user, require_admin

router = APIRouter(prefix="/api/holidays", tags=["Holidays"])


@router.get("", response_model=List[HolidayResponse])
def list_holidays(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Holiday)
    if start_date:
        query = query.filter(Holiday.holiday_date >= start_date)
    if end_date:
        query = query.filter(Holiday.holiday_date <= end_date)
    return query.order_by(Holiday.holiday_date).all()


@router.post("", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
def create_holiday(
    req: HolidayCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(Holiday).filter(Holiday.holiday_date == req.holiday_date).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A holiday is already scheduled for date {req.holiday_date.isoformat()} ({existing.name})"
        )

    holiday = Holiday(
        name=req.name.strip(),
        holiday_date=req.holiday_date,
        holiday_type=req.holiday_type,
        description=req.description.strip() if req.description else None
    )
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return holiday


@router.delete("/{holiday_id}")
def delete_holiday(
    holiday_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    h = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not h:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holiday not found")
    db.delete(h)
    db.commit()
    return {"message": "Holiday removed successfully"}
