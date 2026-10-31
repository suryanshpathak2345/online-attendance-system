"""
Demonstration Data Seeder for Online Attendance Management System
Contains clearly labeled fictional sample data for local development and testing.
"""
from datetime import date, time, timedelta, datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.academic import ClassRoom, Student, Subject, TeacherAssignment
from app.models.session import ClassSession, SessionStatus, Holiday, HolidayType
from app.models.attendance import AttendanceRecord, AttendanceAuditLog, AttendanceStatus
from app.models.personal import PersonalSubject, PersonalRecord
from app.core.security import hash_password


def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "admin@attendease.edu").first():
            print("[INFO] Database already contains demonstration seed data.")
            return

        print("[DEMO SEED] Populating demonstration data...")

        # 1. Administrator
        admin_user = User(
            email="admin@attendease.edu",
            full_name="System Administrator (Demo)",
            hashed_password=hash_password("Admin@Pass2026!"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)

        # 2. Teachers
        teacher1 = User(
            email="prof.sharma@attendease.edu",
            full_name="Prof. Rajesh Sharma",
            hashed_password=hash_password("Teacher@Pass2026!"),
            role=UserRole.TEACHER,
            is_active=True
        )
        teacher2 = User(
            email="dr.patel@attendease.edu",
            full_name="Dr. Priya Patel",
            hashed_password=hash_password("Teacher@Pass2026!"),
            role=UserRole.TEACHER,
            is_active=True
        )
        db.add_all([teacher1, teacher2])
        db.flush()

        # 3. Classes
        class_a = ClassRoom(
            name="B.Tech Computer Science & Engineering",
            section="Section A",
            academic_year="2025-2026",
            description="Third year undergraduate cohort, CSE department."
        )
        class_b = ClassRoom(
            name="B.Tech Computer Science & Engineering",
            section="Section B",
            academic_year="2025-2026",
            description="Third year undergraduate cohort, CSE Section B."
        )
        db.add_all([class_a, class_b])
        db.flush()

        # 4. Subjects
        sub1 = Subject(name="Data Structures & Algorithms", code="CS201", class_id=class_a.id)
        sub2 = Subject(name="Database Management Systems", code="CS202", class_id=class_a.id)
        sub3 = Subject(name="Operating Systems", code="CS203", class_id=class_a.id)
        sub4 = Subject(name="Computer Networks", code="CS204", class_id=class_a.id)
        db.add_all([sub1, sub2, sub3, sub4])
        db.flush()

        # 5. Teacher Assignments
        # Prof. Sharma teaches CS201 (DSA) and CS203 (OS)
        # Dr. Patel teaches CS202 (DBMS) and CS204 (Networks)
        t_assign1 = TeacherAssignment(teacher_id=teacher1.id, subject_id=sub1.id, class_id=class_a.id)
        t_assign2 = TeacherAssignment(teacher_id=teacher2.id, subject_id=sub2.id, class_id=class_a.id)
        t_assign3 = TeacherAssignment(teacher_id=teacher1.id, subject_id=sub3.id, class_id=class_a.id)
        t_assign4 = TeacherAssignment(teacher_id=teacher2.id, subject_id=sub4.id, class_id=class_a.id)
        db.add_all([t_assign1, t_assign2, t_assign3, t_assign4])
        db.flush()

        # 6. Students (10 fictional students)
        demo_students_data = [
            ("Aarav Verma", "CSE-2026-001", "aarav.verma@student.attendease.edu", "STU-1001"),
            ("Diya Sen", "CSE-2026-002", "diya.sen@student.attendease.edu", "STU-1002"),
            ("Rohan Iyer", "CSE-2026-003", "rohan.iyer@student.attendease.edu", "STU-1003"),
            ("Ananya Rao", "CSE-2026-004", "ananya.rao@student.attendease.edu", "STU-1004"),
            ("Kabir Mehta", "CSE-2026-005", "kabir.mehta@student.attendease.edu", "STU-1005"),
            ("Sneha Nair", "CSE-2026-006", "sneha.nair@student.attendease.edu", "STU-1006"),
            ("Vikram Malhotra", "CSE-2026-007", "vikram.malhotra@student.attendease.edu", "STU-1007"),
            ("Pooja Hegde", "CSE-2026-008", "pooja.hegde@student.attendease.edu", "STU-1008"),
            ("Aditya Joshi", "CSE-2026-009", "aditya.joshi@student.attendease.edu", "STU-1009"),
            ("Meera Pillai", "CSE-2026-010", "meera.pillai@student.attendease.edu", "STU-1010"),
        ]

        created_students = []
        for name, roll, email, ident in demo_students_data:
            # Create student user account
            stu_user = User(
                email=email,
                full_name=name,
                hashed_password=hash_password("Student@Pass2026!"),
                role=UserRole.STUDENT,
                is_active=True
            )
            db.add(stu_user)
            db.flush()

            st = Student(
                full_name=name,
                roll_number=roll,
                email=email,
                student_identifier=ident,
                class_id=class_a.id,
                user_id=stu_user.id,
                is_active=True
            )
            db.add(st)
            created_students.append(st)

        db.flush()

        # 7. Holidays
        today = date.today()
        h1 = Holiday(
            name="National Technology Day",
            holiday_date=today - timedelta(days=12),
            holiday_type=HolidayType.INSTITUTIONAL,
            description="Annual institutional science and tech holiday"
        )
        h2 = Holiday(
            name="Autumn Break",
            holiday_date=today + timedelta(days=15),
            holiday_type=HolidayType.INSTITUTIONAL,
            description="Mid-semester institutional break"
        )
        db.add_all([h1, h2])

        # 8. Class Sessions & Sample Attendance Records
        # Create 5 conducted sessions for DSA (CS201)
        for i in range(5, 0, -1):
            sess_date = today - timedelta(days=i * 2)
            session = ClassSession(
                class_id=class_a.id,
                subject_id=sub1.id,
                teacher_id=teacher1.id,
                session_date=sess_date,
                start_time=time(9, 30),
                end_time=time(10, 30),
                topic=f"DSA Module {6 - i}: Advanced Trees & Graphs",
                status=SessionStatus.CONDUCTED,
                is_attendance_submitted=True,
                submitted_at=datetime.utcnow() - timedelta(days=i * 2, hours=-1)
            )
            db.add(session)
            db.flush()

            # Mark attendance for each student
            for s_idx, st in enumerate(created_students):
                # Make student 1 (Aarav) 100% present
                # Student 5 (Kabir) absent on two sessions to show low attendance
                if s_idx == 4 and i in [2, 4]:
                    att_status = AttendanceStatus.ABSENT
                elif s_idx == 2 and i == 3:
                    att_status = AttendanceStatus.HALF_DAY
                elif s_idx == 6 and i in [1, 3]:
                    att_status = AttendanceStatus.ABSENT
                else:
                    att_status = AttendanceStatus.PRESENT

                rec = AttendanceRecord(
                    session_id=session.id,
                    student_id=st.id,
                    status=att_status,
                    remarks="Regular session record",
                    created_at=datetime.utcnow() - timedelta(days=i * 2),
                    updated_at=datetime.utcnow() - timedelta(days=i * 2)
                )
                db.add(rec)

        # Create 1 Conducted Session for DBMS (CS202)
        dbms_session = ClassSession(
            class_id=class_a.id,
            subject_id=sub2.id,
            teacher_id=teacher2.id,
            session_date=today - timedelta(days=1),
            start_time=time(11, 0),
            end_time=time(12, 0),
            topic="DBMS: Relational Normalization (3NF & BCNF)",
            status=SessionStatus.CONDUCTED,
            is_attendance_submitted=True,
            submitted_at=datetime.utcnow() - timedelta(days=1)
        )
        db.add(dbms_session)
        db.flush()
        for st in created_students:
            db.add(AttendanceRecord(
                session_id=dbms_session.id,
                student_id=st.id,
                status=AttendanceStatus.PRESENT
            ))

        # Create 1 Scheduled Session awaiting attendance today!
        today_session = ClassSession(
            class_id=class_a.id,
            subject_id=sub1.id,
            teacher_id=teacher1.id,
            session_date=today,
            start_time=time(14, 0),
            end_time=time(15, 0),
            topic="DSA Lab & Dynamic Programming Problem Solving",
            status=SessionStatus.SCHEDULED,
            is_attendance_submitted=False
        )
        db.add(today_session)

        # Create 1 Cancelled Session
        cancelled_session = ClassSession(
            class_id=class_a.id,
            subject_id=sub3.id,
            teacher_id=teacher1.id,
            session_date=today - timedelta(days=3),
            topic="Operating Systems: Memory Management (Interrupted)",
            status=SessionStatus.CANCELLED,
            is_attendance_submitted=False
        )
        db.add(cancelled_session)

        # 9. Personal Tracker Demonstration Data for Aarav (Student 1)
        aarav_user = db.query(User).filter(User.email == "aarav.verma@student.attendease.edu").first()
        if aarav_user:
            ps1 = PersonalSubject(
                user_id=aarav_user.id,
                name="Competitive Programming Practice",
                code="CP101",
                target_percentage=85.0
            )
            ps2 = PersonalSubject(
                user_id=aarav_user.id,
                name="Full-Stack Web Dev BootCamp",
                code="WEB202",
                target_percentage=90.0
            )
            db.add_all([ps1, ps2])
            db.flush()

            for day_offset in range(1, 4):
                db.add(PersonalRecord(
                    personal_subject_id=ps1.id,
                    record_date=today - timedelta(days=day_offset),
                    status="PRESENT",
                    notes="Completed LeetCode contest"
                ))

        db.commit()
        print("[DEMO SEED] Successfully seeded demonstration data!")
        print("  - Admin:    admin@attendease.edu / Admin@Pass2026!")
        print("  - Teacher:  prof.sharma@attendease.edu / Teacher@Pass2026!")
        print("  - Teacher:  dr.patel@attendease.edu / Teacher@Pass2026!")
        print("  - Student:  aarav.verma@student.attendease.edu / Student@Pass2026! (Roll: CSE-2026-001)")

    except Exception as e:
        db.rollback()
        print(f"[DEMO SEED ERROR] Failed to seed database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
