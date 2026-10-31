import apiClient from './client';

export interface SubjectItem {
  id: number;
  name: string;
  code: string;
  class_id: number;
  created_at: string;
  class_name?: string | null;
  class_section?: string | null;
  assigned_teacher_id?: number | null;
  assigned_teacher_name?: string | null;
}

export interface SubjectCreatePayload {
  name: string;
  code: string;
  class_id: number;
  teacher_id?: number | null;
}

export const subjectsApi = {
  list: async (classId?: number): Promise<SubjectItem[]> => {
    const res = await apiClient.get<SubjectItem[]>('/api/subjects', {
      params: classId ? { class_id: classId } : {},
    });
    return res.data;
  },
  create: async (payload: SubjectCreatePayload): Promise<SubjectItem> => {
    const res = await apiClient.post<SubjectItem>('/api/subjects', payload);
    return res.data;
  },
  assignTeacher: async (teacherId: number, subjectId: number, classId: number): Promise<{ message: string }> => {
    const res = await apiClient.post<{ message: string }>('/api/subjects/assign-teacher', {
      teacher_id: teacherId,
      subject_id: subjectId,
      class_id: classId,
    });
    return res.data;
  },
};
