import apiClient from './client';

export interface ClassSessionItem {
  id: number;
  class_id: number;
  subject_id: number;
  teacher_id: number;
  session_date: string;
  start_time?: string | null;
  end_time?: string | null;
  topic?: string | null;
  status: 'SCHEDULED' | 'CONDUCTED' | 'CANCELLED' | 'HOLIDAY';
  is_attendance_submitted: boolean;
  is_locked: boolean;
  submitted_at?: string | null;
  created_at: string;
  class_name?: string | null;
  class_section?: string | null;
  subject_name?: string | null;
  subject_code?: string | null;
  teacher_name?: string | null;
  total_students: number;
  present_count: number;
  absent_count: number;
  half_day_count: number;
}

export interface SessionCreatePayload {
  class_id: number;
  subject_id: number;
  session_date: string;
  start_time?: string | null;
  end_time?: string | null;
  topic?: string | null;
  status?: string;
  teacher_id?: number | null;
}

export const sessionsApi = {
  list: async (filters: {
    class_id?: number;
    subject_id?: number;
    session_date?: string;
    start_date?: string;
    end_date?: string;
    teacher_id?: number;
  }): Promise<ClassSessionItem[]> => {
    const res = await apiClient.get<ClassSessionItem[]>('/api/sessions', { params: filters });
    return res.data;
  },
  get: async (id: number): Promise<ClassSessionItem> => {
    const res = await apiClient.get<ClassSessionItem>(`/api/sessions/${id}`);
    return res.data;
  },
  create: async (payload: SessionCreatePayload): Promise<ClassSessionItem> => {
    const res = await apiClient.post<ClassSessionItem>('/api/sessions', payload);
    return res.data;
  },
  update: async (id: number, payload: Partial<SessionCreatePayload & { is_locked?: boolean }>): Promise<ClassSessionItem> => {
    const res = await apiClient.patch<ClassSessionItem>(`/api/sessions/${id}`, payload);
    return res.data;
  },
};
