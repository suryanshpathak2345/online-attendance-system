from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.academic import Subject, ClassRoom, TeacherAssignment
from app.models.user import User, UserRole
from app.schemas.academic import SubjectCreate, SubjectUpdate, SubjectResponse, TeacherAssignmentCreate
from app.core.permissions import get_current_user, require_admin

router = APIRouter(prefix="/api/subjects", tags=["Subjects"])


@router.get("", response_model=List[SubjectResponse])
def list_subjects(
    class_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List subjects, optionally filtered by class_id."""
    query = db.query(Subject)
    if class_id:
        query = query.filter(Subject.class_id == class_id)

    subjects = query.order_by(Subject.name).all()
    results = []
    for s in subjects:
        assignment = db.query(TeacherAssignment).filter(
            TeacherAssignment.subject_id == s.id,
            TeacherAssignment.class_id == s.class_id
        ).first()

        results.append(SubjectResponse(
            id=s.id,
            name=s.name,
            code=s.code,
            class_id=s.class_id,
            created_at=s.created_at,
            class_name=s.classroom.name if s.classroom else None,
            class_section=s.classroom.section if s.classroom else None,
            assigned_teacher_id=assignment.teacher_id if assignment else None,
            assigned_teacher_name=assignment.teacher.full_name if assignment and assignment.teacher else None
        ))
    return results


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    req: SubjectCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin-only: Create a subject and optionally assign a teacher."""
    classroom = db.query(ClassRoom).filter(ClassRoom.id == req.class_id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    existing = db.query(Subject).filter(
        Subject.code == req.code.strip().upper(),
        Subject.class_id == req.class_id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Subject code already exists in this class")

    subject = Subject(
        name=req.name.strip(),
        code=req.code.strip().upper(),
        class_id=req.class_id
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)

    teacher_name = None
    if req.teacher_id:
        teacher = db.query(User).filter(User.id == req.teacher_id).first()
        if teacher:
            assignment = TeacherAssignment(
                teacher_id=teacher.id,
                subject_id=subject.id,
                class_id=subject.class_id
            )
            db.add(assignment)
            db.commit()
            teacher_name = teacher.full_name

    return SubjectResponse(
        id=subject.id,
        name=subject.name,
        code=subject.code,
        class_id=subject.class_id,
        created_at=subject.created_at,
        class_name=classroom.name,
        class_section=classroom.section,
        assigned_teacher_id=req.teacher_id,
        assigned_teacher_name=teacher_name
    )


@router.post("/assign-teacher")
def assign_teacher_to_subject(
    req: TeacherAssignmentCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin-only: Assign or reassign a teacher to a subject and class."""
    teacher = db.query(User).filter(User.id == req.teacher_id, User.role == UserRole.TEACHER).first()
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    subject = db.query(Subject).filter(Subject.id == req.subject_id, Subject.class_id == req.class_id).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found for given class")

    # Remove existing assignment if any
    db.query(TeacherAssignment).filter(
        TeacherAssignment.subject_id == req.subject_id,
        TeacherAssignment.class_id == req.class_id
    ).delete()

    assignment = TeacherAssignment(
        teacher_id=req.teacher_id,
        subject_id=req.subject_id,
        class_id=req.class_id
    )
    db.add(assignment)
    db.commit()

    return {"message": f"Assigned {teacher.full_name} to {subject.name}"}
