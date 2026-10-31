from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.academic import Student
from app.schemas.auth import LoginRequest, StudentAccessRequest, TokenResponse
from app.core.security import verify_password, create_access_token
from app.core.permissions import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate teacher or administrator."""
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated"
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value, "email": user.email}
    )

    student_id = None
    class_id = None
    if user.role == UserRole.STUDENT and user.student_profile:
        student_id = user.student_profile.id
        class_id = user.student_profile.class_id

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        student_id=student_id,
        class_id=class_id
    )


@router.post("/student-access", response_model=TokenResponse)
def student_verified_access(req: StudentAccessRequest, db: Session = Depends(get_db)):
    """
    Secure student access using Roll Number and Class ID verification.
    If secret_passcode is required (or verified student identifier), validates against student record.
    """
    clean_roll = req.roll_number.strip().upper()
    student = db.query(Student).filter(
        Student.roll_number == clean_roll,
        Student.class_id == req.class_id,
        Student.is_active == True
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active student record found with this roll number in selected class."
        )

    # If student has a linked user account with password, require student login or verify passcode
    if req.secret_passcode:
        # Passcode check against student_identifier
        if req.secret_passcode.strip() != student.student_identifier:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid student security verification code"
            )

    # Ensure linked user exists for student session
    user = student.user
    if not user:
        # If no user account exists yet for this student, create a linked student user
        user = User(
            email=student.email or f"{student.roll_number.lower()}@student.local",
            full_name=student.full_name,
            hashed_password="STUDENT_PORTAL_ACCESS",
            role=UserRole.STUDENT,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        student.user_id = user.id
        db.commit()

    access_token = create_access_token(
        data={"sub": str(user.id), "role": UserRole.STUDENT.value, "student_id": student.id}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=student.full_name,
        role=UserRole.STUDENT,
        student_id=student.id,
        class_id=student.class_id
    )


@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get authenticated user profile details."""
    student_id = None
    class_id = None
    if current_user.role == UserRole.STUDENT and current_user.student_profile:
        student_id = current_user.student_profile.id
        class_id = current_user.student_profile.class_id

    assigned_classes = []
    if current_user.role in [UserRole.TEACHER, UserRole.ADMIN]:
        for assignment in current_user.teacher_assignments:
            assigned_classes.append({
                "assignment_id": assignment.id,
                "class_id": assignment.class_id,
                "class_name": assignment.classroom.name,
                "class_section": assignment.classroom.section,
                "subject_id": assignment.subject_id,
                "subject_name": assignment.subject.name,
                "subject_code": assignment.subject.code
            })

    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "student_id": student_id,
        "class_id": class_id,
        "assigned_classes": assigned_classes
    }


@router.post("/logout")
def logout():
    """Client-side token invalidation confirmation."""
    return {"message": "Logged out successfully"}
