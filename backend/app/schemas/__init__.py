from app.schemas.auth import LoginRequest, StudentAccessRequest, TokenResponse
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.academic import (
    ClassRoomBase, ClassRoomCreate, ClassRoomUpdate, ClassRoomResponse,
    SubjectBase, SubjectCreate, SubjectUpdate, SubjectResponse,
    StudentBase, StudentCreate, StudentUpdate, StudentResponse,
    TeacherAssignmentCreate, TeacherAssignmentResponse,
)
from app.schemas.session import (
    SessionBase, SessionCreate, SessionUpdate, SessionResponse,
    HolidayBase, HolidayCreate, HolidayResponse,
)
from app.schemas.attendance import (
    SingleStudentAttendance, BatchAttendanceSubmission, AttendanceCorrectionRequest,
    StudentAttendanceMarkingRow, SessionAttendanceSummary, AttendanceRecordResponse,
    AttendanceAuditLogResponse,
)
from app.schemas.report import (
    StudentSubjectSummary, StudentOverallReport,
    ClassAttendanceReportRow, ClassAttendanceReport,
    CalendarDayAttendance,
)
