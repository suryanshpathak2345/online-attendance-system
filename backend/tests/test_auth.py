import pytest
from fastapi import HTTPException, status
from app.routers.auth import login, student_verified_access, get_current_user_profile
from app.schemas.auth import LoginRequest, StudentAccessRequest
from app.models.user import UserRole


def test_valid_teacher_login(db_session, test_data):
    req = LoginRequest(email="test_teacher1@test.edu", password="TestPass123!")
    res = login(req, db_session)
    assert res.email == "test_teacher1@test.edu"
    assert res.role == UserRole.TEACHER
    assert res.access_token is not None


def test_invalid_login_password(db_session, test_data):
    req = LoginRequest(email="test_teacher1@test.edu", password="WrongPassword!")
    with pytest.raises(HTTPException) as exc:
        login(req, db_session)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid email or password" in exc.value.detail


def test_nonexistent_user_login(db_session, test_data):
    req = LoginRequest(email="nobody@test.edu", password="AnyPassword!")
    with pytest.raises(HTTPException) as exc:
        login(req, db_session)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED


def test_student_verified_access(db_session, test_data):
    req = StudentAccessRequest(
        roll_number="STU-01",
        class_id=test_data["classroom"].id
    )
    res = student_verified_access(req, db_session)
    assert res.role == UserRole.STUDENT
    assert res.student_id == test_data["student1"].id
    assert res.access_token is not None


def test_student_access_invalid_roll(db_session, test_data):
    req = StudentAccessRequest(
        roll_number="NONEXISTENT-999",
        class_id=test_data["classroom"].id
    )
    with pytest.raises(HTTPException) as exc:
        student_verified_access(req, db_session)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_get_current_user_profile(db_session, test_data):
    profile = get_current_user_profile(current_user=test_data["teacher1"], db=db_session)
    assert profile["email"] == "test_teacher1@test.edu"
    assert len(profile["assigned_classes"]) >= 1


def test_teacher_login_and_profile_workflow(client, test_data):
    response = client.post(
        "/api/auth/login",
        json={"email": "test_teacher1@test.edu", "password": "TestPass123!"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["role"] == "teacher"
    assert payload["access_token"]

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {payload['access_token']}"},
    )
    assert me_response.status_code == 200
    me = me_response.json()
    assert me["email"] == "test_teacher1@test.edu"
    assert len(me["assigned_classes"]) >= 1


def test_student_self_report_access_is_restricted(client, db_session, test_data):
    session = test_data["session"]
    record = session.attendance_records[0] if session.attendance_records else None
    if record is None:
        from app.models.attendance import AttendanceRecord, AttendanceStatus
        record = AttendanceRecord(
            session_id=session.id,
            student_id=test_data["student1"].id,
            status=AttendanceStatus.PRESENT,
            remarks="On time"
        )
        db_session.add(record)
        db_session.commit()

    login_response = client.post(
        "/api/auth/login",
        json={"email": "student1@test.edu", "password": "TestPass123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    own_report = client.get(
        f"/api/reports/student/{test_data['student1'].id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert own_report.status_code == 200
    own_data = own_report.json()
    assert own_data["student_id"] == test_data["student1"].id
    assert own_data["overall_percentage"] is None or own_data["overall_percentage"] >= 0

    forbidden = client.get(
        f"/api/reports/student/{test_data['student2'].id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert forbidden.status_code == 403
    assert "Access forbidden" in forbidden.json()["detail"]
