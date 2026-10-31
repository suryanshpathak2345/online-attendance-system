import apiClient from './client';

export interface StudentItem {
  id: number;
  full_name: string;
  roll_number: string;
  email?: string | null;
  student_identifier: string;
  class_id: number;
  user_id?: number | null;
  is_active: boolean;
  created_at: string;
  class_name?: string | null;
  class_section?: string | null;
}

export interface StudentCreatePayload {
  full_name: string;
  roll_number: string;
  email?: string;
  student_identifier: string;
  class_id: number;
  is_active?: boolean;
}

export const studentsApi = {
  list: async (classId?: number, search?: string): Promise<StudentItem[]> => {
    const res = await apiClient.get<StudentItem[]>('/api/students', {
      params: {
        ...(classId ? { class_id: classId } : {}),
        ...(search ? { search } : {}),
      },
    });
    return res.data;
  },
  create: async (payload: StudentCreatePayload): Promise<StudentItem> => {
    const res = await apiClient.post<StudentItem>('/api/students', payload);
    return res.data;
  },
  importCsv: async (classId: number, file: File): Promise<{ imported_count: number; errors: string[]; message: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post(`/api/students/import-csv/${classId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};
