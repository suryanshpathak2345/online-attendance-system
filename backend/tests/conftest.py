import pytest
import os
from datetime import date, time, datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.academic import ClassRoom, Student, Subject, TeacherAssignment
from app.models.session import ClassSession, SessionStatus
from app.models.attendance import AttendanceRecord, AttendanceStatus
from app.core.security import hash_password, create_access_token

PREHASHED_PASSWORD = hash_password("TestPass123!")

TEST_DB_PATH = os.path.abspath("test_runner.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass


@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_data(db_session):
    # Clean previous records
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()

    admin = User(
        email="test_admin@test.edu",
        full_name="Test Admin",
        hashed_password=PREHASHED_PASSWORD,
        role=UserRole.ADMIN,
        is_active=True
    )
    teacher1 = User(
        email="test_teacher1@test.edu",
        full_name="Teacher One",
        hashed_password=PREHASHED_PASSWORD,
        role=UserRole.TEACHER,
        is_active=True
    )
    teacher2 = User(
        email="test_teacher2@test.edu",
        full_name="Teacher Two",
        hashed_password=PREHASHED_PASSWORD,
        role=UserRole.TEACHER,
        is_active=True
    )
    db_session.add_all([admin, teacher1, teacher2])
    db_session.flush()

    classroom = ClassRoom(
        name="Computer Science",
        section="Sec A",
        academic_year="2025-2026",
        description="Test Classroom"
    )
    db_session.add(classroom)
    db_session.flush()

    subject = Subject(
        name="Algorithms",
        code="CS101",
        class_id=classroom.id
    )
    db_session.add(subject)
    db_session.flush()

    assignment = TeacherAssignment(
        teacher_id=teacher1.id,
        subject_id=subject.id,
        class_id=classroom.id
    )
    db_session.add(assignment)

    stu_user1 = User(
        email="student1@test.edu",
        full_name="Student One",
        hashed_password=PREHASHED_PASSWORD,
        role=UserRole.STUDENT,
        is_active=True
    )
    stu_user2 = User(
        email="student2@test.edu",
        full_name="Student Two",
        hashed_password=PREHASHED_PASSWORD,
        role=UserRole.STUDENT,
        is_active=True
    )
    db_session.add_all([stu_user1, stu_user2])
    db_session.flush()

    student1 = Student(
        full_name="Student One",
        roll_number="STU-01",
        email="student1@test.edu",
        student_identifier="REG-001",
        class_id=classroom.id,
        user_id=stu_user1.id,
        is_active=True
    )
    student2 = Student(
        full_name="Student Two",
        roll_number="STU-02",
        email="student2@test.edu",
        student_identifier="REG-002",
        class_id=classroom.id,
        user_id=stu_user2.id,
        is_active=True
    )
    db_session.add_all([student1, student2])
    db_session.flush()

    today = date.today()
    session = ClassSession(
        class_id=classroom.id,
        subject_id=subject.id,
        teacher_id=teacher1.id,
        session_date=today,
        start_time=time(10, 0),
        end_time=time(11, 0),
        topic="Sorting Algorithms",
        status=SessionStatus.SCHEDULED,
        is_attendance_submitted=False
    )
    db_session.add(session)
    db_session.commit()

    return {
        "admin": admin,
        "teacher1": teacher1,
        "teacher2": teacher2,
        "classroom": classroom,
        "subject": subject,
        "student1": student1,
        "student2": student2,
        "stu_user1": stu_user1,
        "stu_user2": stu_user2,
        "session": session
    }


def auth_header(user: User) -> dict:
    token = create_access_token(data={"sub": str(user.id), "role": user.role.value, "email": user.email})
    return {"Authorization": f"Bearer {token}"}
