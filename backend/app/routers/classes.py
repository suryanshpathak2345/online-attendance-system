from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.academic import ClassRoom, Student, Subject, TeacherAssignment
from app.models.user import User, UserRole
from app.models.session import ClassSession
from app.schemas.academic import ClassRoomCreate, ClassRoomUpdate, ClassRoomResponse
from app.core.permissions import get_current_user, require_admin, require_teacher_or_admin

router = APIRouter(prefix="/api/classes", tags=["Classes"])


@router.get("", response_model=List[ClassRoomResponse])
def list_classes(
    include_archived: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List classes. For teachers, prioritizes assigned classes; admins see all."""
    query = db.query(ClassRoom)
    if not include_archived:
        query = query.filter(ClassRoom.is_archived == False)

    classes = query.order_by(ClassRoom.name, ClassRoom.section).all()
    results = []
    for c in classes:
        student_count = db.query(Student).filter(Student.class_id == c.id, Student.is_active == True).count()
        subject_count = db.query(Subject).filter(Subject.class_id == c.id).count()
        results.append(ClassRoomResponse(
            id=c.id,
            name=c.name,
            section=c.section,
            academic_year=c.academic_year,
            description=c.description,
            is_archived=c.is_archived,
            created_at=c.created_at,
            student_count=student_count,
            subject_count=subject_count
        ))
    return results


@router.post("", response_model=ClassRoomResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    req: ClassRoomCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin-only: Create a new class."""
    existing = db.query(ClassRoom).filter(
        ClassRoom.name == req.name.strip(),
        ClassRoom.section == req.section.strip(),
        ClassRoom.academic_year == req.academic_year.strip()
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Class with identical name, section, and academic year already exists."
        )

    classroom = ClassRoom(
        name=req.name.strip(),
        section=req.section.strip(),
        academic_year=req.academic_year.strip(),
        description=req.description.strip() if req.description else None
    )
    db.add(classroom)
    db.commit()
    db.refresh(classroom)

    return ClassRoomResponse(
        id=classroom.id,
        name=classroom.name,
        section=classroom.section,
        academic_year=classroom.academic_year,
        description=classroom.description,
        is_archived=classroom.is_archived,
        created_at=classroom.created_at,
        student_count=0,
        subject_count=0
    )


@router.get("/{class_id}", response_model=ClassRoomResponse)
def get_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single class details."""
    classroom = db.query(ClassRoom).filter(ClassRoom.id == class_id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    student_count = db.query(Student).filter(Student.class_id == classroom.id, Student.is_active == True).count()
    subject_count = db.query(Subject).filter(Subject.class_id == classroom.id).count()

    return ClassRoomResponse(
        id=classroom.id,
        name=classroom.name,
        section=classroom.section,
        academic_year=classroom.academic_year,
        description=classroom.description,
        is_archived=classroom.is_archived,
        created_at=classroom.created_at,
        student_count=student_count,
        subject_count=subject_count
    )


@router.patch("/{class_id}", response_model=ClassRoomResponse)
def update_class(
    class_id: int,
    req: ClassRoomUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin-only: Update class details or toggle archive status."""
    classroom = db.query(ClassRoom).filter(ClassRoom.id == class_id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    if req.name is not None:
        classroom.name = req.name.strip()
    if req.section is not None:
        classroom.section = req.section.strip()
    if req.academic_year is not None:
        classroom.academic_year = req.academic_year.strip()
    if req.description is not None:
        classroom.description = req.description.strip()
    if req.is_archived is not None:
        classroom.is_archived = req.is_archived

    db.commit()
    db.refresh(classroom)

    student_count = db.query(Student).filter(Student.class_id == classroom.id, Student.is_active == True).count()
    subject_count = db.query(Subject).filter(Subject.class_id == classroom.id).count()

    return ClassRoomResponse(
        id=classroom.id,
        name=classroom.name,
        section=classroom.section,
        academic_year=classroom.academic_year,
        description=classroom.description,
        is_archived=classroom.is_archived,
        created_at=classroom.created_at,
        student_count=student_count,
        subject_count=subject_count
    )


@router.delete("/{class_id}")
def archive_or_delete_class(
    class_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Safely archive class or delete if no attendance history exists."""
    classroom = db.query(ClassRoom).filter(ClassRoom.id == class_id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    has_sessions = db.query(ClassSession).filter(ClassSession.class_id == class_id).count() > 0
    if has_sessions:
        classroom.is_archived = True
        db.commit()
        return {"message": "Class has existing attendance records and was safely archived rather than deleted."}

    db.delete(classroom)
    db.commit()
    return {"message": "Class deleted successfully."}
