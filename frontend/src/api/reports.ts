import apiClient from './client';

export interface StudentSubjectSummary {
  subject_id: number;
  subject_name: string;
  subject_code: string;
  conducted_sessions: number;
  attended_sessions: number;
  absent_sessions: number;
  half_day_sessions: number;
  attendance_percentage: number | null;
  threshold: number;
  is_below_threshold: boolean;
}

export interface StudentOverallReport {
  student_id: number;
  roll_number: string;
  full_name: string;
  class_id: number;
  class_name: string;
  class_section: string;
  total_conducted: number;
  total_attended: number;
  total_absent: number;
  total_half_day: number;
  overall_percentage: number | null;
  threshold: number;
  is_below_threshold: boolean;
  subject_summaries: StudentSubjectSummary[];
}

export interface ClassAttendanceReportRow {
  student_id: number;
  roll_number: string;
  full_name: string;
  conducted_sessions: number;
  attended_sessions: number;
  absent_sessions: number;
  half_day_sessions: number;
  attendance_percentage: number | null;
  is_below_threshold: boolean;
}

export interface ClassAttendanceReport {
  class_id: number;
  class_name: string;
  class_section: string;
  academic_year: string;
  subject_id?: number | null;
  subject_name?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  threshold: number;
  total_conducted_sessions: number;
  average_attendance_percentage: number | null;
  students_count: number;
  low_attendance_count: number;
  student_rows: ClassAttendanceReportRow[];
}

export interface CalendarDayAttendance {
  date_str: string;
  day: number;
  session_id?: number | null;
  subject_name?: string | null;
  status?: string | null;
  topic?: string | null;
  is_holiday: boolean;
  holiday_name?: string | null;
}

export const reportsApi = {
  getClassReport: async (
    classId: number,
    params?: { subject_id?: number; start_date?: string; end_date?: string; threshold?: number }
  ): Promise<ClassAttendanceReport> => {
    const res = await apiClient.get<ClassAttendanceReport>(`/api/reports/class/${classId}`, { params });
    return res.data;
  },
  getStudentReport: async (
    studentId: number,
    params?: { start_date?: string; end_date?: string; threshold?: number }
  ): Promise<StudentOverallReport> => {
    const res = await apiClient.get<StudentOverallReport>(`/api/reports/student/${studentId}`, { params });
    return res.data;
  },
  getStudentCalendar: async (
    studentId: number,
    year: number,
    month: number,
    subjectId?: number
  ): Promise<CalendarDayAttendance[]> => {
    const res = await apiClient.get<CalendarDayAttendance[]>(`/api/reports/student/${studentId}/calendar`, {
      params: { year, month, ...(subjectId ? { subject_id: subjectId } : {}) },
    });
    return res.data;
  },
  downloadExcel: async (classId: number, subjectId: number, startDate?: string, endDate?: string) => {
    const response = await apiClient.get('/api/reports/export/excel', {
      params: {
        class_id: classId,
        subject_id: subjectId,
        ...(startDate ? { start_date: startDate } : {}),
        ...(endDate ? { end_date: endDate } : {}),
      },
      responseType: 'blob',
    });

    // Extract filename from header or construct fallback
    const disposition = response.headers['content-disposition'];
    let filename = `attendance_class_${classId}_subj_${subjectId}.xlsx`;
    if (disposition && disposition.indexOf('filename=') !== -1) {
      const match = disposition.match(/filename="?([^"]+)"?/);
      if (match && match[1]) filename = match[1];
    }

    // Trigger browser download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
};
