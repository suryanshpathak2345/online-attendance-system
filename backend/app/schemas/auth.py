from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class StudentAccessRequest(BaseModel):
    roll_number: str
    class_id: int
    secret_passcode: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str
    role: UserRole
    student_id: Optional[int] = None
    class_id: Optional[int] = None
