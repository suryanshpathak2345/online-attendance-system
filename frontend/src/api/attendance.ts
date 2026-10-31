import apiClient from './client';

export type AttendanceStatusType = 'PRESENT' | 'ABSENT' | 'HALF_DAY';

export interface StudentRowInSheet {
  student_id: number;
  roll_number: string;
  full_name: string;
  student_identifier: string;
  status: AttendanceStatusType | null;
  remarks?: string | null;
  record_id?: number | null;
}

export interface AttendanceSheetResponse {
  session_id: number;
  class_id: number;
  class_name: string;
  class_section: string;
  subject_id: number;
  subject_name: string;
  subject_code: string;
  session_date: string;
  topic?: string | null;
  is_attendance_submitted: boolean;
  is_locked: boolean;
  total_enrolled: number;
  present_count: number;
  absent_count: number;
  half_day_count: number;
  not_marked_count: number;
  absent_students: Array<{
    student_id: number;
    roll_number: string;
    full_name: string;
    student_identifier: string;
    status: AttendanceStatusType;
    remarks?: string | null;
  }>;
  students: StudentRowInSheet[];
}

export interface SubmitAttendancePayload {
  records: Array<{
    student_id: number;
    status: AttendanceStatusType;
    remarks?: string | null;
  }>;
}

export interface AttendanceAuditLogItem {
  id: number;
  session_id: number;
  student_id: number;
  student_name: string;
  student_roll: string;
  previous_status: string;
  new_status: string;
  reason?: string | null;
  changed_by_user_id: number;
  changed_by_name: string;
  changed_at: string;
}

export const attendanceApi = {
  getSheet: async (sessionId: number): Promise<AttendanceSheetResponse> => {
    const res = await apiClient.get<AttendanceSheetResponse>(`/api/attendance/session/${sessionId}/sheet`);
    return res.data;
  },
  submit: async (sessionId: number, payload: SubmitAttendancePayload) => {
    const res = await apiClient.post(`/api/attendance/session/${sessionId}/submit`, payload);
    return res.data;
  },
  correctRecord: async (recordId: number, newStatus: AttendanceStatusType, reason?: string) => {
    const res = await apiClient.patch(`/api/attendance/record/${recordId}/correct`, {
      new_status: newStatus,
      reason,
    });
    return res.data;
  },
  getAuditLogs: async (sessionId: number): Promise<AttendanceAuditLogItem[]> => {
    const res = await apiClient.get<AttendanceAuditLogItem[]>(`/api/attendance/session/${sessionId}/audit-logs`);
    return res.data;
  },
};
