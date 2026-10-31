from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io

from app.database import get_db
from app.models.academic import Student, ClassRoom
from app.models.user import User, UserRole
from app.schemas.academic import StudentCreate, StudentUpdate, StudentResponse
from app.core.permissions import get_current_user, require_admin, require_teacher_or_admin

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.get("", response_model=List[StudentResponse])
def list_students(
    class_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List students with optional class filter and search."""
    query = db.query(Student).filter(Student.is_active == True)
    if class_id:
        query = query.filter(Student.class_id == class_id)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter((Student.full_name.ilike(s)) | (Student.roll_number.ilike(s)))

    students = query.order_by(Student.roll_number).all()
    results = []
    for st in students:
        results.append(StudentResponse(
            id=st.id,
            full_name=st.full_name,
            roll_number=st.roll_number,
            email=st.email,
            student_identifier=st.student_identifier,
            class_id=st.class_id,
            user_id=st.user_id,
            is_active=st.is_active,
            created_at=st.created_at,
            class_name=st.classroom.name if st.classroom else None,
            class_section=st.classroom.section if st.classroom else None
        ))
    return results


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    req: StudentCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin-only: Add a student to a class."""
    classroom = db.query(ClassRoom).filter(ClassRoom.id == req.class_id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    roll_clean = req.roll_number.strip().upper()
    existing_roll = db.query(Student).filter(
        Student.roll_number == roll_clean,
        Student.class_id == req.class_id
    ).first()
    if existing_roll:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roll number {roll_clean} already exists in this class"
        )

    identifier_clean = req.student_identifier.strip().upper()
    existing_id = db.query(Student).filter(Student.student_identifier == identifier_clean).first()
    if existing_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student identifier {identifier_clean} already registered"
        )

    student = Student(
        full_name=req.full_name.strip(),
        roll_number=roll_clean,
        email=req.email.strip().lower() if req.email else None,
        student_identifier=identifier_clean,
        class_id=req.class_id,
        is_active=req.is_active
    )
    db.add(student)
    db.commit()
    db.refresh(student)

    return StudentResponse(
        id=student.id,
        full_name=student.full_name,
        roll_number=student.roll_number,
        email=student.email,
        student_identifier=student.student_identifier,
        class_id=student.class_id,
        user_id=student.user_id,
        is_active=student.is_active,
        created_at=student.created_at,
        class_name=classroom.name,
        class_section=classroom.section
    )


@router.post("/import-csv/{class_id}")
async def import_students_csv(
    class_id: int,
    file: UploadFile = File(...),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin-only: Import students from CSV file (columns: roll_number, full_name, email, identifier)."""
    classroom = db.query(ClassRoom).filter(ClassRoom.id == class_id).first()
    if not classroom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    content = await file.read()
    decoded = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))

    created_count = 0
    errors = []

    for row_idx, row in enumerate(reader, start=1):
        full_name = row.get("full_name") or row.get("name") or row.get("Full Name")
        roll_number = row.get("roll_number") or row.get("roll") or row.get("Roll Number")
        email = row.get("email") or row.get("Email")
        identifier = row.get("identifier") or row.get("id") or row.get("Student ID") or roll_number

        if not full_name or not roll_number:
            errors.append(f"Row {row_idx}: Missing name or roll number")
            continue

        clean_roll = roll_number.strip().upper()
        clean_id = identifier.strip().upper() if identifier else clean_roll

        # Check existing roll in class
        exists = db.query(Student).filter(Student.roll_number == clean_roll, Student.class_id == class_id).first()
        if exists:
            errors.append(f"Row {row_idx}: Roll number {clean_roll} already exists")
            continue

        student = Student(
            full_name=full_name.strip(),
            roll_number=clean_roll,
            email=email.strip().lower() if email else None,
            student_identifier=clean_id,
            class_id=class_id,
            is_active=True
        )
        db.add(student)
        created_count += 1

    db.commit()
    return {
        "imported_count": created_count,
        "errors": errors,
        "message": f"Successfully imported {created_count} students."
    }


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    return StudentResponse(
        id=student.id,
        full_name=student.full_name,
        roll_number=student.roll_number,
        email=student.email,
        student_identifier=student.student_identifier,
        class_id=student.class_id,
        user_id=student.user_id,
        is_active=student.is_active,
        created_at=student.created_at,
        class_name=student.classroom.name if student.classroom else None,
        class_section=student.classroom.section if student.classroom else None
    )


@router.patch("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    req: StudentUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    if req.full_name is not None:
        student.full_name = req.full_name.strip()
    if req.roll_number is not None:
        student.roll_number = req.roll_number.strip().upper()
    if req.email is not None:
        student.email = req.email.strip().lower()
    if req.student_identifier is not None:
        student.student_identifier = req.student_identifier.strip().upper()
    if req.is_active is not None:
        student.is_active = req.is_active
    if req.class_id is not None:
        student.class_id = req.class_id

    db.commit()
    db.refresh(student)

    return StudentResponse(
        id=student.id,
        full_name=student.full_name,
        roll_number=student.roll_number,
        email=student.email,
        student_identifier=student.student_identifier,
        class_id=student.class_id,
        user_id=student.user_id,
        is_active=student.is_active,
        created_at=student.created_at,
        class_name=student.classroom.name if student.classroom else None,
        class_section=student.classroom.section if student.classroom else None
    )
